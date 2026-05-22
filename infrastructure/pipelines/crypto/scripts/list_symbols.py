"""Print which pairs a given exchange lists, optionally filtered by quote currency.

    python scripts/list_symbols.py --exchange kraken --quote USD
"""
from __future__ import annotations

import argparse

from crypto_lean.client import ExchangeClient


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exchange", required=True,
                   choices=["coinbase", "kraken"])
    p.add_argument("--quote", default=None, help="Filter by quote currency (USD/USDT/USDC).")
    p.add_argument("--base", default=None, help="Filter by base currency (BTC/ETH/...).")
    args = p.parse_args()

    client = ExchangeClient(exchange=args.exchange)
    symbols = client._client.symbols or []
    if args.quote:
        symbols = [s for s in symbols if s.endswith(f"/{args.quote.upper()}")]
    if args.base:
        symbols = [s for s in symbols if s.startswith(f"{args.base.upper()}/")]
    for s in sorted(symbols):
        print(s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
