"""SQL extraction functions for CRSP daily data, distributions, and name history."""

import pandas as pd
from .connection import get_connection


def extract_daily_prices(permnos, start='1998-01-01', end='2026-12-31'):
    """Extract daily price data from crsp.dsf.

    Returns DataFrame with columns:
        permno, date, openprc, askhi, bidlo, prc, vol, ret, retx, cfacpr, cfacshr
    """
    conn = get_connection()
    sql = """
        SELECT permno, date, openprc, askhi, bidlo, prc, vol, ret, retx,
               cfacpr, cfacshr
        FROM crsp.dsf
        WHERE permno IN %(permnos)s
          AND date BETWEEN %(start)s AND %(end)s
        ORDER BY permno, date
    """
    df = conn.raw_sql(sql, params={
        'permnos': tuple(permnos),
        'start': start,
        'end': end,
    })
    df['date'] = pd.to_datetime(df['date'])
    return df


def extract_distributions(permnos):
    """Extract distribution events from crsp.dsedist.

    Returns DataFrame with columns:
        permno, exdt, distcd, divamt, facpr, facshr
    """
    conn = get_connection()
    sql = """
        SELECT permno, exdt, distcd, divamt, facpr, facshr
        FROM crsp.dsedist
        WHERE permno IN %(permnos)s
        ORDER BY permno, exdt
    """
    df = conn.raw_sql(sql, params={'permnos': tuple(permnos)})
    df['exdt'] = pd.to_datetime(df['exdt'])
    return df


def extract_name_history(permnos):
    """Extract name/ticker history from crsp.dsenames.

    Returns DataFrame with columns:
        permno, ticker, namedt, nameendt, primexch, exchcd
    """
    conn = get_connection()
    sql = """
        SELECT permno, ticker, namedt, nameendt, primexch, exchcd
        FROM crsp.dsenames
        WHERE permno IN %(permnos)s
        ORDER BY permno, namedt
    """
    df = conn.raw_sql(sql, params={'permnos': tuple(permnos)})
    df['namedt'] = pd.to_datetime(df['namedt'])
    df['nameendt'] = pd.to_datetime(df['nameendt'])
    return df
