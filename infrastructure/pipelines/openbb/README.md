# OpenBB

[OpenBB Platform](https://docs.openbb.co/) — open-source research toolkit. Installed in the workspace venv as `openbb`.

## Usage

OpenBB is best used **interactively in research notebooks**, not as a batch pipeline. It exposes many data providers (yfinance, FMP, FRED, SEC, etc.) through a single API.

```python
from openbb import obb

# Equity history (yfinance, no key needed)
data = obb.equity.price.historical("AAPL", start_date="2020-01-01", provider="yfinance")
df = data.to_df()

# Macro data (FRED, requires API key)
gdp = obb.economy.gdp.real(country="united_states", provider="fred")

# SEC filings
filings = obb.equity.fundamental.filings(symbol="AAPL", provider="sec")
```

## When to reach for OpenBB vs edgartools vs WRDS

| Need | Use |
|---|---|
| Quick exploratory market data in a notebook | **OpenBB** |
| Macro / FRED / IMF data | **OpenBB** |
| Authoritative SEC fundamentals (batch extraction) | **edgartools** (`infrastructure/edgar/`) |
| CRSP-quality equity prices + 30-stock equity universe | **WRDS** (`infrastructure/wrds/`) |
| Final backtest data | **QuantConnect cloud** |

## API keys

OpenBB providers like FMP, Polygon, FRED require API keys. Configure via:
```bash
openbb-api configure
```
or in a notebook: `obb.account.login(pat="...")` (for OpenBB Hub) / set environment variables.

**Do not commit API keys.** Use `~/.openbb_platform/user_settings.json` (gitignored) or env vars.

## No pipeline (yet)

There's no batch extractor here — OpenBB shines interactively. If a recurring data pull becomes useful (e.g. nightly macro snapshot), add a `pipeline.py` here following the edgartools pattern.
