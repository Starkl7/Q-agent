"""Neo4j driver singleton and session context manager."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from neo4j import Driver, GraphDatabase, Session

from agent_graph_system.config import cfg

log = logging.getLogger(__name__)

_driver: Driver | None = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            cfg.neo4j.uri,
            auth=(cfg.neo4j.user, cfg.neo4j.password),
        )
        log.info("Neo4j driver initialised at %s", cfg.neo4j.uri)
    return _driver


def close_driver() -> None:
    global _driver
    if _driver:
        _driver.close()
        _driver = None


@contextmanager
def session() -> Generator[Session, None, None]:
    with get_driver().session(database=cfg.neo4j.database) as s:
        yield s


def verify_connectivity() -> bool:
    try:
        get_driver().verify_connectivity()
        return True
    except Exception as exc:
        log.warning("Neo4j connectivity check failed: %s", exc)
        return False
