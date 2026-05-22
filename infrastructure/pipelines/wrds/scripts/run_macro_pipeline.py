"""CLI for WRDS macro, FX, and factor exports."""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wrds_lean.connection import close_connection, set_connection_profile
from wrds_lean.macro import (
    extract_ff_factors,
    extract_fx_daily,
    extract_global_factors,
    extract_rates_daily,
    publish_csv,
)

LEAN_DATA = os.path.join(os.path.dirname(__file__), '..', 'lean-data')


def _write_if_requested(name, enabled, extractor, subdir, filename):
    if not enabled:
        return None
    print(f"\n=== Extracting {name} ===")
    df = extractor()
    print(f"  {len(df):,} rows")
    path = publish_csv(df, LEAN_DATA, subdir, filename)
    print(f"  Written to {path}")
    return path


def main():
    parser = argparse.ArgumentParser(description='WRDS macro and factor pipeline')
    parser.add_argument('--profile', default=None,
                        help='Named WRDS profile from .wrds_profiles.json')
    parser.add_argument('--start', default=None, help='Start date YYYY-MM-DD')
    parser.add_argument('--end', default=None, help='End date YYYY-MM-DD')
    parser.add_argument('--fx', action='store_true', help='Export FRB daily FX')
    parser.add_argument('--rates', action='store_true', help='Export FRB daily rates')
    parser.add_argument('--ff', action='store_true',
                        help='Export Fama-French daily factors')
    parser.add_argument('--ff5', action='store_true',
                        help='Export Fama-French five-factor daily data')
    parser.add_argument('--global-factor', action='store_true',
                        help='Export contrib_global_factor rows')
    parser.add_argument('--countries', nargs='+', default=None,
                        help='Global factor country codes, e.g. USA GBR JPN')
    parser.add_argument('--permnos', nargs='+', type=int, default=None,
                        help='Global factor PERMNO filter')
    parser.add_argument('--columns', nargs='+', default=None,
                        help='Global factor columns to export')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit global factor rows for exploration')
    args = parser.parse_args()

    if not any([args.fx, args.rates, args.ff, args.ff5, args.global_factor]):
        args.fx = args.rates = args.ff = args.ff5 = True

    set_connection_profile(args.profile)
    if args.profile:
        print(f"Using WRDS profile: {args.profile}")

    t0 = time.time()
    _write_if_requested(
        'FRB daily FX',
        args.fx,
        lambda: extract_fx_daily(args.start, args.end),
        'macro',
        'frb_fx_daily.csv',
    )
    _write_if_requested(
        'FRB daily rates',
        args.rates,
        lambda: extract_rates_daily(args.start, args.end),
        'macro',
        'frb_rates_daily.csv',
    )
    _write_if_requested(
        'Fama-French daily factors',
        args.ff,
        lambda: extract_ff_factors(args.start, args.end, five_factor=False),
        'factors',
        'ff_factors_daily.csv',
    )
    _write_if_requested(
        'Fama-French five factors',
        args.ff5,
        lambda: extract_ff_factors(args.start, args.end, five_factor=True),
        'factors',
        'ff_fivefactors_daily.csv',
    )
    _write_if_requested(
        'global factor panel',
        args.global_factor,
        lambda: extract_global_factors(
            start=args.start,
            end=args.end,
            countries=args.countries,
            permnos=args.permnos,
            columns=args.columns,
            limit=args.limit,
        ),
        'factors',
        'global_factor.csv',
    )

    close_connection()
    print(f"\n=== Macro pipeline complete in {time.time() - t0:.1f}s ===")


if __name__ == '__main__':
    main()
