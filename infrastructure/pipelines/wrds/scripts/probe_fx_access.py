"""Probe FX-related WRDS schemas/tables across both profiles.

Tests SELECT access on the standard candidate FX sources and reports
what each profile can actually read. No data is persisted.

Usage:
    python scripts/probe_fx_access.py
    python scripts/probe_fx_access.py --profile <additional>
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wrds_lean.connection import close_connection, get_connection, set_connection_profile

# Candidate FX schemas/tables on WRDS. We probe each: existence + SELECT.
# Table format: (schema, table, note)
CANDIDATES = [
    # Federal Reserve H.10 daily FX rates (most common WRDS FX source)
    ('frb', 'rates_daily', 'FRB H.10 daily exchange rates (USD pairs)'),
    ('frb', 'rates_monthly', 'FRB H.10 monthly exchange rates'),
    ('frb', 'fx', 'FRB FX (legacy)'),
    # Compustat currency translation rates
    ('comp', 'exrt_dly', 'Compustat daily currency translation rates'),
    ('comp', 'exrt_mth', 'Compustat monthly currency translation rates'),
    ('comp_global_daily', 'exrt_dly', 'Compustat Global daily FX'),
    ('comp_global_daily', 'g_exrt_dly', 'Compustat Global daily FX (g_ prefix)'),
    # OptionMetrics FX (sometimes bundled)
    ('optionm_global', 'fx_rates', 'OptionMetrics global FX rates'),
    # WRDS-curated FX
    ('wrdsapps', 'fx_rates', 'WRDS apps FX rates'),
    # Bloomberg-derived (if subscribed)
    ('bvd', 'fx_rates', 'Bureau van Dijk FX'),
    # CRSP currency (rare)
    ('crsp', 'currency', 'CRSP currency table'),
]

# Schemas to list tables from when accessible, to discover anything we missed.
SCHEMAS_TO_LIST = ['frb', 'comp', 'comp_global_daily', 'optionm_global', 'wrdsapps']


def probe_table(conn, schema, table):
    """Try a 1-row SELECT and return (status, columns, sample) or (status, error, None)."""
    qualified = f'{schema}.{table}'
    try:
        df = conn.raw_sql(f'SELECT * FROM {qualified} LIMIT 1')
    except Exception as exc:
        msg = str(exc).strip().split('\n')[0]
        if 'permission denied' in msg.lower():
            return ('DENIED', msg, None)
        if 'does not exist' in msg.lower() or 'undefined table' in msg.lower():
            return ('MISSING', msg, None)
        return ('ERROR', msg, None)

    if df is None or df.empty:
        return ('EMPTY', list(df.columns) if df is not None else [], None)
    return ('OK', list(df.columns), df.iloc[0].to_dict())


def list_schema_tables(conn, schema):
    """Return up to 200 table names in a schema, or empty list if denied/missing."""
    sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %(schema)s
        ORDER BY table_name
        LIMIT 500
    """
    try:
        df = conn.raw_sql(sql, params={'schema': schema})
    except Exception:
        return []
    return df['table_name'].tolist() if df is not None else []


def find_fx_named_tables(conn, schema):
    """Find tables in a schema with names suggesting FX/currency content."""
    tables = list_schema_tables(conn, schema)
    keywords = ('fx', 'forex', 'exrt', 'exrate', 'currenc', 'rates_dail', 'rates_mont')
    return [t for t in tables if any(k in t.lower() for k in keywords)]


def run_probe(profile_name):
    print(f'\n{"=" * 70}')
    print(f'WRDS FX probe — profile: {profile_name}')
    print(f'{"=" * 70}\n')

    set_connection_profile(profile_name)
    conn = get_connection()

    # 1. Probe known candidate tables
    print('--- Candidate FX tables ---')
    accessible = []
    for schema, table, note in CANDIDATES:
        status, info, sample = probe_table(conn, schema, table)
        marker = {'OK': '[OK]    ', 'DENIED': '[DENY]  ', 'MISSING': '[NONE]  ',
                  'EMPTY': '[EMPTY] ', 'ERROR': '[ERR]   '}[status]
        print(f'{marker} {schema}.{table:30s}  {note}')
        if status == 'OK':
            accessible.append((schema, table, info, sample))
        elif status not in ('MISSING',):
            print(f'         -> {info[:120]}')

    # 2. Discovery: scan likely schemas for FX-named tables we missed
    print('\n--- Discovery: FX-named tables in common schemas ---')
    for schema in SCHEMAS_TO_LIST:
        matches = find_fx_named_tables(conn, schema)
        if matches:
            print(f'{schema}: {matches}')
        else:
            print(f'{schema}: (no fx/currency/exrt-named tables visible)')

    # 3. Detail accessible tables
    if accessible:
        print('\n--- Accessible table details ---')
        for schema, table, columns, sample in accessible:
            print(f'\n{schema}.{table}')
            print(f'  columns ({len(columns)}): {columns[:20]}'
                  f'{"..." if len(columns) > 20 else ""}')
            if sample:
                preview = {k: sample[k] for k in list(sample.keys())[:6]}
                print(f'  sample row (first 6 cols): {preview}')
    else:
        print('\nNo candidate FX tables were SELECTable on this profile.')

    close_connection()
    return accessible


def main():
    parser = argparse.ArgumentParser(description='Probe WRDS FX data access')
    parser.add_argument(
        '--profile',
        default=None,
        help='Single profile to probe (default: probe both ncsu and skema)',
    )
    args = parser.parse_args()

    profiles = [args.profile] if args.profile else ['ncsu', 'skema']

    results = {}
    for profile in profiles:
        try:
            results[profile] = run_probe(profile)
        except Exception as exc:
            print(f'\n[FATAL] Profile {profile} failed to connect: {exc}')
            results[profile] = []

    print(f'\n{"=" * 70}')
    print('Summary')
    print(f'{"=" * 70}')
    for profile, accessible in results.items():
        if accessible:
            tables = ', '.join(f'{s}.{t}' for s, t, _, _ in accessible)
            print(f'  {profile}: {len(accessible)} table(s) accessible -> {tables}')
        else:
            print(f'  {profile}: no FX tables accessible')


if __name__ == '__main__':
    main()
