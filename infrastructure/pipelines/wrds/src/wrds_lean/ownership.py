"""Institutional ownership exports from Thomson Reuters 13F."""

import os

import pandas as pd

from .connection import get_connection


def extract_13f_holdings(tickers=None, start=None, end=None, min_shares=None):
    """Pull manager-level 13F holdings from tr_13f.s34."""
    conn = get_connection()
    clauses = []
    params = {}
    if tickers:
        clauses.append('ticker IN %(tickers)s')
        params['tickers'] = tuple(t.upper() for t in tickers)
    if start:
        clauses.append('rdate >= %(start)s')
        params['start'] = start
    if end:
        clauses.append('rdate <= %(end)s')
        params['end'] = end
    if min_shares is not None:
        clauses.append('shares >= %(min_shares)s')
        params['min_shares'] = min_shares

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ''
    sql = f"""
        SELECT
            rdate, fdate, mgrno, mgrname, typecode, country,
            ticker, cusip, stkname, shares, change, prc,
            shrout1, shrout2, sole, shared, no
        FROM tr_13f.s34
        {where}
        ORDER BY rdate, ticker, mgrno
    """
    return conn.raw_sql(sql, params=params)


def build_13f_summary(holdings):
    """Aggregate 13F holdings by report date and ticker."""
    if holdings.empty:
        return pd.DataFrame(columns=[
            'ReportDate', 'Ticker', 'CUSIP', 'IssuerName', 'ManagerCount',
            'TotalShares', 'TotalMarketValue', 'SharesOutstanding',
            'InstitutionalOwnershipPct',
        ])

    df = holdings.copy()
    df['market_value'] = df['shares'] * df['prc']
    grouped = (
        df.groupby(['rdate', 'ticker'], dropna=False)
        .agg(
            CUSIP=('cusip', 'first'),
            IssuerName=('stkname', 'first'),
            ManagerCount=('mgrno', 'nunique'),
            TotalShares=('shares', 'sum'),
            TotalMarketValue=('market_value', 'sum'),
            SharesOutstanding=('shrout1', 'max'),
        )
        .reset_index()
    )
    grouped['InstitutionalOwnershipPct'] = (
        grouped['TotalShares'] / grouped['SharesOutstanding']
    )
    return (
        grouped.rename(columns={'rdate': 'ReportDate', 'ticker': 'Ticker'})
        [[
            'ReportDate', 'Ticker', 'CUSIP', 'IssuerName', 'ManagerCount',
            'TotalShares', 'TotalMarketValue', 'SharesOutstanding',
            'InstitutionalOwnershipPct',
        ]]
        .sort_values(['Ticker', 'ReportDate'])
        .reset_index(drop=True)
    )


def publish_13f_holdings(df, lean_data_dir):
    out_dir = os.path.join(lean_data_dir, 'alternative', 'ownership')
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, '13f_holdings.csv')
    df.to_csv(filepath, index=False, date_format='%Y-%m-%d')
    return filepath


def publish_13f_summary(df, lean_data_dir):
    out_dir = os.path.join(lean_data_dir, 'alternative', 'ownership')
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, '13f_summary.csv')
    df.to_csv(filepath, index=False, date_format='%Y-%m-%d')
    return filepath
