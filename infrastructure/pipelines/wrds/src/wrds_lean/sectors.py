"""Sector classification from Compustat.

Extracts GICS sector codes from Compustat, maps to Morningstar sector codes
(as used by QuantConnect fundamentals), and publishes a static sector map.

Output: lean-data/alternative/sectors/sector_map.csv
Format: Ticker,GICSSector,GICSIndustryGroup,GICSIndustry,GICSSubIndustry,MorningstarSectorCode,MorningstarSectorName,SIC
"""

import os

import pandas as pd

from .connection import get_connection

# GICS sector code -> Morningstar sector code mapping
# GICS: https://www.msci.com/our-solutions/indexes/gics
# Morningstar: https://www.quantconnect.com/docs/v2/writing-algorithms/securities/asset-classes/us-equity/requesting-data/fundamentals
GICS_TO_MORNINGSTAR = {
    10: (309, "Energy"),
    15: (101, "Basic Materials"),
    20: (310, "Industrials"),
    25: (102, "Consumer Cyclical"),
    30: (205, "Consumer Defensive"),
    35: (206, "Healthcare"),
    40: (103, "Financial Services"),
    45: (311, "Technology"),
    50: (308, "Communication Services"),
    55: (207, "Utilities"),
    60: (104, "Real Estate"),
}


def extract_sectors(tickers):
    """Extract GICS sector classifications from Compustat.

    Args:
        tickers: List of ticker strings

    Returns:
        DataFrame with columns: ticker, gvkey, gsector, gind, gsubind, sic, conm
    """
    conn = get_connection()

    sql = """
        SELECT s.tic AS ticker, c.gvkey, c.gsector, c.gind, c.gsubind, c.sic, c.conm
        FROM comp.security s
        JOIN comp.company c ON s.gvkey = c.gvkey
        WHERE s.tic IN %(tickers)s
          AND s.iid = '01'
        ORDER BY s.tic
    """
    df = conn.raw_sql(sql, params={'tickers': tuple(tickers)})
    return df


def transform_sector_map(sectors_df):
    """Transform Compustat GICS data to include Morningstar sector codes.

    Args:
        sectors_df: DataFrame from extract_sectors()

    Returns:
        DataFrame with added MorningstarSectorCode and MorningstarSectorName columns
    """
    df = sectors_df.copy()

    # Parse GICS sector (first 2 digits of gsector)
    df['gsector_int'] = pd.to_numeric(df['gsector'], errors='coerce').astype('Int64')

    # Map to Morningstar
    df['MorningstarSectorCode'] = df['gsector_int'].map(
        lambda x: GICS_TO_MORNINGSTAR.get(x, (None, None))[0] if pd.notna(x) else None
    ).astype('Int64')

    df['MorningstarSectorName'] = df['gsector_int'].map(
        lambda x: GICS_TO_MORNINGSTAR.get(x, (None, None))[1] if pd.notna(x) else None
    )

    # Clean up output columns
    result = df[[
        'ticker', 'conm', 'gsector', 'gind', 'gsubind', 'sic',
        'MorningstarSectorCode', 'MorningstarSectorName'
    ]].copy()
    result.columns = [
        'Ticker', 'CompanyName', 'GICSSector', 'GICSIndustryGroup',
        'GICSSubIndustry', 'SIC', 'MorningstarSectorCode', 'MorningstarSectorName'
    ]

    return result


def publish_sector_map(sector_df, lean_data_dir=None):
    """Write sector map CSV to lean-data.

    Args:
        sector_df: DataFrame from transform_sector_map()
        lean_data_dir: Base lean-data directory

    Returns:
        Path to the written file
    """
    if lean_data_dir is None:
        lean_data_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'lean-data'
        )

    sector_dir = os.path.join(lean_data_dir, 'alternative', 'sectors')
    os.makedirs(sector_dir, exist_ok=True)

    filepath = os.path.join(sector_dir, 'sector_map.csv')
    sector_df.to_csv(filepath, index=False)

    return filepath
