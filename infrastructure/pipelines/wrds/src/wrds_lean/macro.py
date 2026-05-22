"""Macro, FX, and factor data exports from WRDS."""

import os

from .connection import get_connection


def _date_filter(column, start=None, end=None):
    clauses = []
    params = {}
    if start:
        clauses.append(f"{column} >= %(start)s")
        params['start'] = start
    if end:
        clauses.append(f"{column} <= %(end)s")
        params['end'] = end
    return clauses, params


def _select_table(schema, table, date_col='date', start=None, end=None, columns=None):
    conn = get_connection()
    selected = ', '.join(columns) if columns else '*'
    clauses, params = _date_filter(date_col, start, end)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ''
    sql = f"""
        SELECT {selected}
        FROM {schema}.{table}
        {where}
        ORDER BY {date_col}
    """
    return conn.raw_sql(sql, params=params)


def extract_fx_daily(start=None, end=None):
    """Pull Federal Reserve H.10 daily FX rates."""
    return _select_table('frb', 'fx_daily', start=start, end=end)


def extract_rates_daily(start=None, end=None):
    """Pull Federal Reserve daily interest rates and credit spreads."""
    return _select_table('frb', 'rates_daily', start=start, end=end)


def extract_ff_factors(start=None, end=None, five_factor=False):
    """Pull daily Fama-French factors."""
    table = 'fivefactors_daily' if five_factor else 'factors_daily'
    return _select_table('ff', table, start=start, end=end)


def extract_global_factors(
    start=None,
    end=None,
    countries=None,
    permnos=None,
    columns=None,
    limit=None,
):
    """Pull Jensen-Kelly-Pedersen global factor rows.

    The source is very wide and large. Callers should pass countries, permnos,
    columns, or a limit when exploring.
    """
    conn = get_connection()
    default_cols = [
        'id', 'permno', 'gvkey', 'iid', 'excntry', 'date', 'eom',
        'curcd', 'fx', 'me', 'prc', 'ret', 'ret_exc',
        'gics', 'sic', 'ff49', 'ret_1_0', 'ret_12_1',
        'market_equity', 'book_equity', 'net_income', 'sales',
    ]
    selected_cols = columns or default_cols
    clauses, params = _date_filter('date', start, end)
    if countries:
        clauses.append('excntry IN %(countries)s')
        params['countries'] = tuple(countries)
    if permnos:
        clauses.append('permno IN %(permnos)s')
        params['permnos'] = tuple(int(p) for p in permnos)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ''
    limit_clause = f'LIMIT {int(limit)}' if limit else ''
    sql = f"""
        SELECT {', '.join(selected_cols)}
        FROM contrib_global_factor.global_factor
        {where}
        ORDER BY date, permno
        {limit_clause}
    """
    return conn.raw_sql(sql, params=params)


def publish_csv(df, lean_data_dir, subdir, filename):
    """Publish a DataFrame to a CSV under lean-data/alternative."""
    out_dir = os.path.join(lean_data_dir, 'alternative', subdir)
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, filename)
    df.to_csv(filepath, index=False, date_format='%Y-%m-%d')
    return filepath
