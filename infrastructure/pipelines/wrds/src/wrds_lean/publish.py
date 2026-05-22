"""Publish LEAN-format files: daily bar zips, factor files, map files."""

import os
import zipfile
import io


LEAN_DATA_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'lean-data')
DAILY_DIR = os.path.join(LEAN_DATA_ROOT, 'equity', 'usa', 'daily')
FACTOR_DIR = os.path.join(LEAN_DATA_ROOT, 'equity', 'usa', 'factor_files')
MAP_DIR = os.path.join(LEAN_DATA_ROOT, 'equity', 'usa', 'map_files')


def _ensure_dirs():
    for d in [DAILY_DIR, FACTOR_DIR, MAP_DIR]:
        os.makedirs(d, exist_ok=True)


def publish_daily_bar(ticker, df):
    """Write daily bar DataFrame as {ticker}.zip containing {ticker}.csv.

    DataFrame must have columns: date_str, open, high, low, close, volume
    Written as CSV with no header.
    """
    _ensure_dirs()
    ticker = ticker.lower()

    # Build CSV content
    lines = []
    for _, row in df.iterrows():
        lines.append(
            f"{row['date_str']},{row['open']},{row['high']},"
            f"{row['low']},{row['close']},{row['volume']}"
        )
    csv_content = '\n'.join(lines) + '\n'

    # Write zip
    zip_path = os.path.join(DAILY_DIR, f'{ticker}.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f'{ticker}.csv', csv_content)

    return zip_path


def publish_factor_file(ticker, df):
    """Write factor file DataFrame as {ticker}.csv.

    DataFrame must have columns: date_str, price_factor, split_factor, ref_price
    Written as CSV with no header.
    """
    _ensure_dirs()
    ticker = ticker.lower()

    lines = []
    for _, row in df.iterrows():
        # Format: ref_price can be 0 (sentinel) or a price
        ref = row['ref_price']
        if ref == 0:
            ref_str = '0'
        else:
            ref_str = f"{ref}"
        lines.append(
            f"{row['date_str']},{row['price_factor']},{row['split_factor']},{ref_str}"
        )
    csv_content = '\n'.join(lines) + '\n'

    path = os.path.join(FACTOR_DIR, f'{ticker}.csv')
    with open(path, 'w') as f:
        f.write(csv_content)

    return path


def publish_map_file(ticker, df):
    """Write map file DataFrame as {ticker}.csv.

    DataFrame must have columns: date_str, ticker, exchange
    Written as CSV with no header.
    """
    _ensure_dirs()
    ticker = ticker.lower()

    lines = []
    for _, row in df.iterrows():
        lines.append(f"{row['date_str']},{row['ticker']},{row['exchange']}")
    csv_content = '\n'.join(lines) + '\n'

    path = os.path.join(MAP_DIR, f'{ticker}.csv')
    with open(path, 'w') as f:
        f.write(csv_content)

    return path
