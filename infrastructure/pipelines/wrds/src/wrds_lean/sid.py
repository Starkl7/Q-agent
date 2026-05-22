"""LEAN SecurityIdentifier generation for equity symbols.

Ports the essential parts of LEAN's C# SecurityIdentifier.Generate() to Python
so we can produce valid SID strings for ETF universe files.

The SID string format is: "{SYMBOL} {base36_encoded_properties}"
where properties encodes the first trade date, market, and security type.
"""

import datetime
import os

# LEAN SecurityIdentifier bit-packing constants
# Layout: {put/call:1}{oa-date:5}{style:1}{strike:6}{strike-scale:2}{market:3}{security-type:2}
_SECURITY_TYPE_OFFSET = 1
_SECURITY_TYPE_WIDTH = 100
_MARKET_OFFSET = _SECURITY_TYPE_OFFSET * _SECURITY_TYPE_WIDTH       # 100
_MARKET_WIDTH = 1000
_STRIKE_SCALE_OFFSET = _MARKET_OFFSET * _MARKET_WIDTH               # 100_000
_STRIKE_SCALE_WIDTH = 100
_STRIKE_OFFSET = _STRIKE_SCALE_OFFSET * _STRIKE_SCALE_WIDTH         # 10_000_000
_STRIKE_WIDTH = 1_000_000
_OPTION_STYLE_OFFSET = _STRIKE_OFFSET * _STRIKE_WIDTH               # 10_000_000_000_000
_OPTION_STYLE_WIDTH = 10
_DAYS_OFFSET = _OPTION_STYLE_OFFSET * _OPTION_STYLE_WIDTH           # 100_000_000_000_000
_DAYS_WIDTH = 100_000

# Market codes (from LEAN Market.cs)
_MARKET_USA = 1

# Security types (from LEAN SecurityType enum)
_SECURITY_TYPE_EQUITY = 1

# OA date base: December 30, 1899
_OA_BASE = datetime.date(1899, 12, 30)

_BASE36_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _to_oa_date(dt):
    """Convert a date to OLE Automation date (days since 1899-12-30)."""
    if isinstance(dt, datetime.datetime):
        dt = dt.date()
    return (dt - _OA_BASE).days


def _encode_base36(n):
    """Encode an unsigned integer as a base-36 string (uppercase)."""
    if n == 0:
        return "0"
    chars = []
    while n > 0:
        chars.append(_BASE36_CHARS[n % 36])
        n //= 36
    return "".join(reversed(chars))


def generate_equity_sid(symbol, first_date):
    """Generate a LEAN SecurityIdentifier string for a US equity.

    Args:
        symbol: Ticker symbol (e.g. "AAPL")
        first_date: First trade date as datetime.date (from map file first row)

    Returns:
        SID string like "AAPL R735QTJ8XC9X"
    """
    oa_date = _to_oa_date(first_date)
    properties = (
        oa_date * _DAYS_OFFSET
        + _MARKET_USA * _MARKET_OFFSET
        + _SECURITY_TYPE_EQUITY
    )
    return f"{symbol.upper()} {_encode_base36(properties)}"


def get_first_date_from_map_file(map_file_path):
    """Read the first date from a LEAN map file.

    Map files have format: date,ticker,exchange (no header).
    The first row's date is the first trade date used for SID generation.
    """
    with open(map_file_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            date_str = line.split(",")[0]
            return datetime.datetime.strptime(date_str, "%Y%m%d").date()
    raise ValueError(f"Empty map file: {map_file_path}")


def build_sid_lookup(map_files_dir):
    """Build a {ticker_upper: sid_string} dict from all map files in a directory.

    Args:
        map_files_dir: Path to equity/usa/map_files/ directory

    Returns:
        Dict mapping e.g. "AAPL" -> "AAPL R735QTJ8XC9X"
    """
    lookup = {}
    if not os.path.isdir(map_files_dir):
        return lookup

    for filename in os.listdir(map_files_dir):
        if not filename.endswith(".csv"):
            continue
        ticker = filename.replace(".csv", "").upper()
        path = os.path.join(map_files_dir, filename)
        try:
            first_date = get_first_date_from_map_file(path)
            lookup[ticker] = generate_equity_sid(ticker, first_date)
        except (ValueError, IndexError):
            continue

    return lookup
