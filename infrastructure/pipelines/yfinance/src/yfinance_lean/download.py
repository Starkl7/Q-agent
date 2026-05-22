"""Download OHLCV history and corporate action data from Yahoo Finance."""

import yfinance as yf
import pandas as pd


EXCHANGE_MAP = {
    'NMS': 'Q',      # NASDAQ Global Select
    'NGM': 'Q',      # NASDAQ Global Market
    'NCM': 'Q',      # NASDAQ Capital Market
    'NYQ': 'N',      # NYSE
    'NYSEArca': 'P', # NYSE Arca
    'PCX': 'P',      # Pacific Exchange (Arca legacy)
    'ASE': 'A',      # AMEX
    'BTS': 'Q',      # BATS (treat as NASDAQ-like)
}


def download_history(ticker, start='1990-01-01', end=None):
    """Download raw (unadjusted) OHLCV + dividends + splits for a ticker.

    Returns a DataFrame with columns:
        Open, High, Low, Close, Volume, Dividends, Stock Splits
    Index: timezone-naive DatetimeIndex (dates only, market open days).
    Prices are unadjusted (auto_adjust=False).
    """
    t = yf.Ticker(ticker)
    df = t.history(start=start, end=end, auto_adjust=False, actions=True)
    if df.empty:
        raise ValueError(f"No data returned for {ticker!r}")

    # Drop timezone info; keep date component only
    df.index = pd.to_datetime(df.index).normalize().tz_localize(None)
    df.index.name = 'Date'

    # Keep only the columns we need (yfinance may return Adj Close etc.)
    keep = [c for c in ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            if c in df.columns]
    df = df[keep].copy()

    # Fill missing action columns with 0
    for col in ['Dividends', 'Stock Splits']:
        if col not in df.columns:
            df[col] = 0.0

    return df


def get_exchange_code(ticker):
    """Return the LEAN exchange code (N/Q/P/A) for a ticker.

    Falls back to 'Q' if the exchange cannot be determined.
    """
    try:
        info = yf.Ticker(ticker).info
        exch = info.get('exchange', '')
        return EXCHANGE_MAP.get(exch, 'Q')
    except Exception:
        return 'Q'
