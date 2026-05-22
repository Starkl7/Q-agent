"""yfinance-to-LEAN daily equity data pipeline.

Usage:
    python scripts/run_pipeline.py --tickers AAPL MSFT SPY
    python scripts/run_pipeline.py --tickers AAPL --start 2010-01-01
    python scripts/run_pipeline.py --tickers AAPL --start 2010-01-01 --end 2024-12-31
    python scripts/run_pipeline.py --tickers AAPL --output /path/to/lean-data

Output goes to infrastructure/yfinance/lean-data/ by default.
Point lean.json at that directory for local backtests:
    "data-folder": "~/Documents/Q-agent/infrastructure/yfinance/lean-data"
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yfinance_lean.download import download_history, get_exchange_code
from yfinance_lean.transform import transform_daily_bars, transform_factor_file, transform_map_file
from yfinance_lean.publish import publish_daily_bar, publish_factor_file, publish_map_file, LEAN_DATA_ROOT


def run_pipeline(tickers, start, end, output_root=None):
    if output_root:
        # Allow caller to redirect output
        import yfinance_lean.publish as _pub
        _pub.LEAN_DATA_ROOT = output_root
        _pub.DAILY_DIR  = os.path.join(output_root, 'equity', 'usa', 'daily')
        _pub.FACTOR_DIR = os.path.join(output_root, 'equity', 'usa', 'factor_files')
        _pub.MAP_DIR    = os.path.join(output_root, 'equity', 'usa', 'map_files')

    t0 = time.time()
    successes, failures = [], []

    for ticker in tickers:
        print(f"\n=== {ticker} ===")
        try:
            # 1. Download
            df = download_history(ticker, start=start, end=end)
            n_days = len(df)
            span = f"{df.index[0].date()} to {df.index[-1].date()}"
            n_splits = int((df['Stock Splits'] > 0).sum())
            n_divs   = int((df['Dividends']    > 0).sum())
            print(f"  {n_days} trading days ({span}), {n_splits} splits, {n_divs} dividends")

            # 2. Exchange code
            exchange = get_exchange_code(ticker)

            # 3. Transform
            bars_df   = transform_daily_bars(df)
            factor_df = transform_factor_file(df)
            map_df    = transform_map_file(ticker, exchange, df.index[0], df.index[-1])

            # 4. Publish
            zip_path    = publish_daily_bar(ticker, bars_df)
            factor_path = publish_factor_file(ticker, factor_df)
            map_path    = publish_map_file(ticker, map_df)

            print(f"  -> {zip_path}")
            print(f"  -> {factor_path}  ({len(factor_df)} rows)")
            print(f"  -> {map_path}")
            successes.append(ticker)

        except Exception as exc:
            print(f"  ERROR: {exc}")
            failures.append(ticker)

    elapsed = time.time() - t0
    print(f"\n=== Done in {elapsed:.1f}s — {len(successes)} ok, {len(failures)} failed ===")
    if failures:
        print(f"  Failed: {failures}")


def main():
    parser = argparse.ArgumentParser(description='yfinance-to-LEAN daily equity pipeline')
    parser.add_argument('--tickers', nargs='+', required=True,
                        help='One or more ticker symbols to download and convert')
    parser.add_argument('--start', default='1990-01-01',
                        help='Start date (default: 1990-01-01)')
    parser.add_argument('--end', default=None,
                        help='End date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--output', default=None,
                        help='Override output root directory (default: lean-data/ next to this package)')
    args = parser.parse_args()

    run_pipeline(args.tickers, args.start, args.end, output_root=args.output)


if __name__ == '__main__':
    main()
