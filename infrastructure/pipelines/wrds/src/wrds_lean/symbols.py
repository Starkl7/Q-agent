"""Universe definition and PERMNO resolution from CRSP."""

from .connection import get_connection

# 30-stock equity universe + SPY + SGOV
UNIVERSE = [
    "AAPL", "AMGN", "AXP", "BA", "CAT", "CRM",
    "CSCO", "CVX", "DIS", "DOW", "GS", "HD",
    "HON", "IBM", "INTC", "JNJ", "JPM", "KO",
    "MCD", "MMM", "MRK", "MSFT", "NKE", "PG",
    "TRV", "UNH", "V", "VZ", "WBA", "WMT",
    "SPY", "SGOV",
]


def resolve_permnos(tickers=None):
    """Query crsp.dsenames for all name periods for given tickers.

    Returns DataFrame with columns: permno, ticker, namedt, nameendt, primexch, exchcd
    """
    if tickers is None:
        tickers = UNIVERSE
    conn = get_connection()
    sql = """
        SELECT permno, ticker, namedt, nameendt, primexch, exchcd
        FROM crsp.dsenames
        WHERE ticker IN %(tickers)s
        ORDER BY ticker, nameendt DESC
    """
    return conn.raw_sql(sql, params={'tickers': tuple(tickers)})


def get_current_permnos(tickers=None):
    """Return {ticker: permno} dict using the most recent name period.

    Also prints warnings for tickers not found in CRSP.
    """
    if tickers is None:
        tickers = UNIVERSE
    df = resolve_permnos(tickers)
    # Take the most recent name period per ticker
    current = (df.sort_values('nameendt', ascending=False)
               .drop_duplicates('ticker')
               .set_index('ticker')['permno']
               .to_dict())
    missing = [t for t in tickers if t not in current]
    if missing:
        print(f"WARNING: Tickers not found in CRSP dsenames: {missing}")
    return current
