# Decisions

Project architecture decisions and the reason for each decision.

## LEAN Cloud Push — Large CSV as Embedded Python Module Chunks (2026-05-12)

When a data CSV is too large to push to QuantConnect cloud (LEAN has a ~64KB per-file limit), embed it as compressed base64 chunks split across multiple `.py` files:

```python
# Build time: compress + split
import gzip, base64, math, pandas as pd
df = pd.read_csv('data.csv')
b64 = base64.b64encode(gzip.compress(df.to_csv(index=False).encode())).decode()
MAX = 55_000  # chars per chunk file
n = math.ceil(len(b64) / MAX)
for i in range(n):
    with open(f'data_chunk_{i}.py', 'w') as f:
        f.write(f'DATA = (\n    "{"".join([chr(0)])}"\n)\n')  # fill with actual chunk

# Runtime loader in data_loader.py
from data_chunk_0 import DATA as _C0
import gzip, base64
from io import StringIO
import pandas as pd

def load_data():
    b64 = _C0  # + _C1 + ... for multiple chunks
    return pd.read_csv(StringIO(gzip.decompress(base64.b64decode(b64)).decode()))
```

Use case: `PiotroskiFScore/earnings_data.py` ships IBES earnings dates (~300 KB compressed to ~4 chunk files) with the algorithm. `lean cloud push` follows the import graph and includes all chunk files.

## infrastructure/marimo and infrastructure/pipelines/wrds — embedded repos collapsed (2026-05-15)

These two directories used to be separate Git repositories with their own histories; their `.git` directories were removed so their files now live directly in `Q-agent`. To track them independently again, re-init Git in those directories and add a remote.

## Crypto writer: merge-on-write + atomic swap (2026-05-14)

`infrastructure/pipelines/crypto/src/crypto_lean/writer.py` uses merge-on-write for daily zips and atomic `os.replace()` for all writes. Reason: concurrent agents pulling different date ranges were overwriting each other's files. New data wins on date-key conflicts. Minute zips (one file per day) only get the atomic swap — they can't interleave data from different ranges.

## Embed Small Reference Data in Config, Not Files (2026-05-15)

For small reference datasets (< 1 MB, typical: < 50 KB), embed directly in Python dicts/constants rather than loading from ObjectStore or local files.

**Why**:
- Local LEAN backtests run in Docker with different filesystem mount points (host `/Users/.../data/` ≠ Docker `/LeanCLI/...`)
- ObjectStore is empty in local backtests unless pre-populated (requires prior run or manual setup)
- Embedded data works identically across local, Docker, cloud, and live trading — no path resolution issues

**Example**: Fed rate hike probability timeseries (31 observations, 559 bytes)
```python
# domain/config.py
FED_HIKE_PROBABILITIES = {
    date(2026, 4, 15): 0.145,
    date(2026, 4, 16): 0.145,
    # ... all 31 dates
}

# models/alpha.py
from domain.config import FED_HIKE_PROBABILITIES
self._fed_prob_lookup = FED_HIKE_PROBABILITIES
```

**When to use**: Reference data that is:
- Updated infrequently (< monthly)
- Small (< 50 KB uncompressed)
- Non-sensitive

**For larger data**: Use base64 chunks (see "LEAN Cloud Push" decision above) or cloud-specific ObjectStore loading.
