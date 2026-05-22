"""Thin ccxt wrapper for pulling OHLCV across Binance, Coinbase, Kraken."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Iterable

import ccxt
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

DEFAULT_PAIRS: list[str] = [
    "BTC/USD", "BTC/USDT", "BTC/USDC",
    "ETH/USD", "ETH/USDT", "ETH/USDC",
    "SOL/USD", "SOL/USDT", "SOL/USDC",
]

# ccxt exchange IDs per the user-facing names.
EXCHANGE_IDS: dict[str, str] = {
    "coinbase": "coinbase",
    "kraken": "kraken",
}

# Conservative per-exchange request pacing (seconds between requests).
REQUEST_PACING: dict[str, float] = {
    "coinbase": 0.20,
    "kraken": 1.10,
}


@dataclass
class ExchangeClient:
    """Single-exchange OHLCV fetcher."""

    exchange: str
    api_key: str | None = None
    api_secret: str | None = None

    def __post_init__(self) -> None:
        if self.exchange not in EXCHANGE_IDS:
            raise ValueError(
                f"Unknown exchange {self.exchange!r}. "
                f"Expected one of: {sorted(EXCHANGE_IDS)}"
            )
        ccxt_id = EXCHANGE_IDS[self.exchange]
        cfg: dict = {"enableRateLimit": True}
        env_prefix = self.exchange.upper()
        key = self.api_key or os.getenv(f"{env_prefix}_API_KEY")
        secret = self.api_secret or os.getenv(f"{env_prefix}_API_SECRET")
        if key and secret:
            cfg["apiKey"] = key
            cfg["secret"] = secret
        self._client: ccxt.Exchange = getattr(ccxt, ccxt_id)(cfg)
        self._client.load_markets()
        self._pacing = REQUEST_PACING.get(self.exchange, 1.0)

    def supported_pairs(self, pairs: Iterable[str]) -> list[str]:
        """Filter `pairs` down to the ones this exchange actually lists."""
        listed = set(self._client.symbols or [])
        return [p for p in pairs if p in listed]

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    def fetch_ohlcv_page(
        self,
        symbol: str,
        timeframe: str,
        since_ms: int,
        limit: int = 1000,
    ) -> list[list]:
        time.sleep(self._pacing)
        return self._client.fetch_ohlcv(symbol, timeframe=timeframe,
                                        since=since_ms, limit=limit)

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
    ) -> pd.DataFrame:
        """Paginated OHLCV fetch. Returns a UTC-indexed DataFrame.

        Columns: open, high, low, close, volume.
        """
        if symbol not in (self._client.symbols or []):
            raise ValueError(f"{self.exchange} does not list {symbol}")

        start = start or pd.Timestamp("2017-01-01", tz="UTC")
        end = end or pd.Timestamp.utcnow()
        if start.tz is None:
            start = start.tz_localize("UTC")
        if end.tz is None:
            end = end.tz_localize("UTC")

        timeframe_ms = self._client.parse_timeframe(timeframe) * 1000
        since_ms = int(start.timestamp() * 1000)
        end_ms = int(end.timestamp() * 1000)
        rows: list[list] = []

        while since_ms < end_ms:
            batch = self.fetch_ohlcv_page(symbol, timeframe, since_ms)
            if not batch:
                break
            rows.extend(batch)
            last_ts = batch[-1][0]
            next_since = last_ts + timeframe_ms
            if next_since <= since_ms:
                break
            since_ms = next_since
            if len(batch) < 100:
                break

        if not rows:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        df = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
        df = df.drop_duplicates(subset="ts").sort_values("ts")
        df["datetime"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
        df = df[(df["datetime"] >= start) & (df["datetime"] <= end)]
        df = df.set_index("datetime")[["open", "high", "low", "close", "volume"]]
        return df
