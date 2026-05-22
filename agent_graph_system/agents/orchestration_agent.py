"""Orchestration agent: coordinates other agents in response to graph events."""

from __future__ import annotations

import logging
from typing import Any

from agent_graph_system.agents.base_agent import BaseAgent
from agent_graph_system.graph.backend import query

log = logging.getLogger(__name__)


class OrchestrationAgent(BaseAgent):
    name = "OrchestrationAgent"
    role = "orchestration"

    def run(self, **kwargs) -> Any:
        """
        Inspect the graph for issues and dispatch remediation tasks.
        Current rules:
          - Stale datasets → log for re-ingestion
          - Failed pipelines → log for restart
        """
        actions: list[dict] = []
        log.info("[OrchestrationAgent] scanning graph for remediation tasks")
        try:
            stale = query(
                "MATCH (d:Dataset) WHERE d.status = 'stale' RETURN d.name AS name, d.source AS source"
            )
            for ds in stale:
                actions.append({"action": "reingest_dataset", "target": ds["name"], "source": ds["source"]})
                log.info("[OrchestrationAgent] queuing reingest for: %s", ds["name"])

            failed_pipelines = query(
                "MATCH (p:Pipeline) WHERE p.status = 'failed' RETURN p.name AS name"
            )
            for p in failed_pipelines:
                actions.append({"action": "restart_pipeline", "target": p["name"]})
                log.info("[OrchestrationAgent] queuing restart for pipeline: %s", p["name"])

            self._mark_idle()
        except Exception as exc:
            self._mark_error(str(exc))
            raise
        return {"actions": actions}
