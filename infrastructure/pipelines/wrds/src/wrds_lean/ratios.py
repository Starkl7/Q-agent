"""WRDS financial ratio exports."""

import os

from .connection import get_connection


DEFAULT_RATIO_COLUMNS = [
    'ticker', 'permno', 'gvkey', 'public_date', 'adate', 'qdate',
    'capei', 'bm', 'evm', 'pe_op_basic', 'pe_op_dil', 'pe_exi', 'pe_inc',
    'ps', 'pcf', 'npm', 'gpm', 'roa', 'roe', 'roce', 'gprof',
    'debt_ebitda', 'de_ratio', 'intcov', 'cash_ratio', 'quick_ratio',
    'curr_ratio', 'at_turn', 'accrual', 'ret_crsp', 'mktcap', 'price',
    'ptb', 'divyield', 'gsector', 'gicdesc',
]


def extract_financial_ratios(tickers=None, start=None, end=None, columns=None):
    """Pull precomputed WRDS financial ratios and ticker identifiers."""
    conn = get_connection()
    selected = columns or DEFAULT_RATIO_COLUMNS
    ratio_cols = [c for c in selected if c not in {'ticker'}]
    select_parts = ['id.ticker'] + [f'fr.{c}' for c in ratio_cols]
    clauses = []
    params = {}
    if tickers:
        clauses.append('id.ticker IN %(tickers)s')
        params['tickers'] = tuple(t.upper() for t in tickers)
    if start:
        clauses.append('fr.public_date >= %(start)s')
        params['start'] = start
    if end:
        clauses.append('fr.public_date <= %(end)s')
        params['end'] = end
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ''
    sql = f"""
        SELECT {', '.join(select_parts)}
        FROM wrdsapps_finratio.firm_ratio fr
        LEFT JOIN wrdsapps_finratio.id id
            ON fr.permno = id.permno
        {where}
        ORDER BY id.ticker, fr.public_date
    """
    return conn.raw_sql(sql, params=params)


def publish_financial_ratios(df, lean_data_dir):
    out_dir = os.path.join(lean_data_dir, 'alternative', 'fundamentals')
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, 'wrds_financial_ratios.csv')
    df.to_csv(filepath, index=False, date_format='%Y-%m-%d')
    return filepath
