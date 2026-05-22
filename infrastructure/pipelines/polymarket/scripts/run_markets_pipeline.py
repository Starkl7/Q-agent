"""Snapshot Polymarket markets (metadata only) under a tag filter.

Default filter: crypto + macro + elections (see DEFAULT_TAG_FILTER).

Examples:

    python scripts/run_markets_pipeline.py
    python scripts/run_markets_pipeline.py --filter all
    python scripts/run_markets_pipeline.py --filter crypto bitcoin ethereum
    python scripts/run_markets_pipeline.py --include-closed
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from tqdm import tqdm

from polymarket_lean import DEFAULT_TAG_FILTER, GammaClient, write_markets_csv


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
LEAN_ROOT = ROOT / "lean-data" / "alternative" / "polymarket"
RAW_ROOT = ROOT / "data" / "raw" / "markets"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--filter", nargs="*", default=list(DEFAULT_TAG_FILTER),
        help="Tag slugs to keep. Pass 'all' to disable filtering.",
    )
    p.add_argument("--include-closed", action="store_true",
                   help="Also include closed/resolved markets.")
    p.add_argument("--max-pages", type=int, default=None,
                   help="Cap pagination for quick smoke tests.")
    p.add_argument(
        "--snapshot", action="store_true",
        help="Also write a dated snapshot under markets_history/<YYYYMMDD>.csv.",
    )
    return p.parse_args()


def main() -> int:
    load_dotenv(ROOT / ".env")
    args = parse_args()

    filter_tags: tuple[str, ...]
    if len(args.filter) == 1 and args.filter[0].lower() == "all":
        filter_tags = ()
    else:
        filter_tags = tuple(args.filter)

    print(
        f"Filtering on tags: {filter_tags or '(no filter — all markets)'}",
        file=sys.stderr,
    )

    client = GammaClient()
    kept: list[dict] = []
    seen = 0
    for market in tqdm(
        client.iter_markets(
            active=None,
            closed=None if args.include_closed else False,
            max_pages=args.max_pages,
        ),
        desc="markets",
    ):
        seen += 1
        if filter_tags and not client.market_matches_filter(market, filter_tags):
            continue
        kept.append(market)

    print(f"\nScanned {seen} markets, kept {len(kept)} after filter.",
          file=sys.stderr)

    out_path = LEAN_ROOT / "markets.csv"
    n = write_markets_csv(kept, out_path)
    print(f"Wrote {n} rows → {out_path}", file=sys.stderr)

    if args.snapshot:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        snap_path = LEAN_ROOT / "markets_history" / f"{stamp}.csv"
        write_markets_csv(kept, snap_path)
        print(f"Wrote snapshot → {snap_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
