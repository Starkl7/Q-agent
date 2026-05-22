"""Monitoring agent: watches datasets and pipelines for staleness."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from agent_graph_system.agents.base_agent import BaseAgent
from agent_graph_system.graph.neo4j import graph_models as gm
from agent_graph_system.graph.backend import query

log = logging.getLogger(__name__)

STALENESS_HOURS: dict[str, int] = {
    "WRDS": 24,
    "Bloomberg": 24,
    "Crypto": 1,
    "Polymarket": 4,
    "EDGAR": 168,  # 1 week
    "YFinance": 24,
}


class MonitoringAgent(BaseAgent):
    name = "MonitoringAgent"
    role = "monitoring"

    def run(self, **kwargs) -> Any:
        log.info("[MonitoringAgent] checking dataset freshness")
        results = {"stale_marked": [], "errors": []}
        try:
            datasets = query("MATCH (d:Dataset) RETURN d.name AS name, d.source AS source, d.last_updated AS last_updated")
            for ds in datasets:
                source = ds.get("source", "")
                sla_hours = STALENESS_HOURS.get(source, 48)
                last_updated_str = ds.get("last_updated")
                if not last_updated_str:
                    continue
                try:
                    last_updated = datetime.fromisoformat(last_updated_str)
                    if datetime.utcnow() - last_updated > timedelta(hours=sla_hours):
                        gm.upsert_dataset(ds["name"], source=source, status="stale")
                        results["stale_marked"].append(ds["name"])
                        log.warning("[MonitoringAgent] marked stale: %s", ds["name"])
                except ValueError:
                    results["errors"].append(ds["name"])

            gm.agent_monitors(self.name, "Dataset", "name", "*")
            self._mark_idle()
        except Exception as exc:
            self._mark_error(str(exc))
            raise
        return results
