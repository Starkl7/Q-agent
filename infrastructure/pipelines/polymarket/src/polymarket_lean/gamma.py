"""Polymarket Gamma API client — market metadata + tag filtering.

Endpoints used:
    GET  https://gamma-api.polymarket.com/markets?limit=...&offset=...
    GET  https://gamma-api.polymarket.com/events?...

No auth required for read.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Iterator

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

GAMMA_BASE = "https://gamma-api.polymarket.com"

# Tag slugs we keep when running with --filter default.
# Polymarket exposes tag slugs on each market under `events[].tags[].slug`.
DEFAULT_TAG_FILTER: tuple[str, ...] = (
    "crypto",
    "bitcoin",
    "ethereum",
    "solana",
    "macro",
    "economics",
    "fed",
    "inflation",
    "elections",
    "politics",
    "us-elections",
    "trump",
    "biden",
)


@dataclass
class GammaClient:
    base_url: str = GAMMA_BASE
    pacing_s: float = 0.20
    timeout_s: float = 30.0

    def __post_init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "polymarket-lean/0.1"})

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        time.sleep(self.pacing_s)
        r = self._session.get(f"{self.base_url}{path}", params=params,
                              timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()

    def iter_markets(
        self,
        limit_per_page: int = 500,
        max_pages: int | None = None,
        active: bool | None = None,
        closed: bool | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield raw market dicts. Paginates until exhausted."""
        offset = 0
        page = 0
        while True:
            params: dict[str, Any] = {"limit": limit_per_page, "offset": offset}
            if active is not None:
                params["active"] = str(active).lower()
            if closed is not None:
                params["closed"] = str(closed).lower()
            batch = self._get("/markets", params=params)
            if not batch:
                return
            for m in batch:
                yield m
            page += 1
            if max_pages and page >= max_pages:
                return
            if len(batch) < limit_per_page:
                return
            offset += limit_per_page

    @staticmethod
    def market_tags(market: dict[str, Any]) -> set[str]:
        """Pull the union of tag slugs from a market's events."""
        tags: set[str] = set()
        for ev in market.get("events", []) or []:
            for t in ev.get("tags", []) or []:
                slug = t.get("slug")
                if slug:
                    tags.add(slug.lower())
        return tags

    @classmethod
    def market_matches_filter(
        cls, market: dict[str, Any], filter_slugs: tuple[str, ...]
    ) -> bool:
        if not filter_slugs:
            return True
        return bool(cls.market_tags(market) & set(s.lower() for s in filter_slugs))
