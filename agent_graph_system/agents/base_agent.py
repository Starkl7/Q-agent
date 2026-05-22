"""Abstract base class for all graph agents."""

from __future__ import annotations

import abc
import logging
from datetime import datetime
from typing import Any

from agent_graph_system.graph.neo4j import graph_models as gm

log = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    name: str
    role: str

    def __init__(self) -> None:
        gm.upsert_agent(self.name, role=self.role, status="active",
                        last_seen=datetime.utcnow().isoformat())
        log.info("[%s] registered in graph", self.name)

    @abc.abstractmethod
    def run(self, **kwargs) -> Any:
        ...

    def _mark_idle(self) -> None:
        gm.merge_node("Agent", "name", self.name,
                      {"status": "idle", "last_seen": datetime.utcnow().isoformat()})

    def _mark_error(self, msg: str) -> None:
        gm.merge_node("Agent", "name", self.name,
                      {"status": "error", "last_error": msg, "last_seen": datetime.utcnow().isoformat()})
        log.error("[%s] error: %s", self.name, msg)
