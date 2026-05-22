"""CLI for WRDS financial ratio exports."""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wrds_lean.connection import close_connection, set_connection_profile
from wrds_lean.ratios import extract_financial_ratios, publish_financial_ratios
from wrds_lean.symbols import UNIVERSE

LEAN_DATA = os.path.join(os.path.dirname(__file__), '..', 'lean-data')


def main():
    parser = argparse.ArgumentParser(description='WRDS financial ratios pipeline')
    parser.add_argument('--profile', default=None,
                        help='Named WRDS profile from .wrds_profiles.json')
    parser.add_argument('--tickers', nargs='+', default=None,
                        help='Tickers to pull (default: 30-stock universe)')
    parser.add_argument('--start', default=None, help='Start public date YYYY-MM-DD')
    parser.add_argument('--end', default=None, help='End public date YYYY-MM-DD')
    parser.add_argument('--columns', nargs='+', default=None,
                        help='Override output columns from firm_ratio plus ticker')
    args = parser.parse_args()

    set_connection_profile(args.profile)
    if args.profile:
        print(f"Using WRDS profile: {args.profile}")

    tickers = args.tickers or list(UNIVERSE)
    t0 = time.time()

    print(f"=== Extracting financial ratios for {len(tickers)} tickers ===")
    ratios = extract_financial_ratios(
        tickers=tickers,
        start=args.start,
        end=args.end,
        columns=args.columns,
    )
    print(f"  {len(ratios):,} rows")

    path = publish_financial_ratios(ratios, LEAN_DATA)
    print(f"  Written to {path}")

    close_connection()
    print(f"\n=== Financial ratios pipeline complete in {time.time() - t0:.1f}s ===")


if __name__ == '__main__':
    main()
