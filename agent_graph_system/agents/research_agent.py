"""Research agent: discovers new relationships in the graph via GraphRAG."""

from __future__ import annotations

import logging
from typing import Any

from agent_graph_system.agents.base_agent import BaseAgent
from agent_graph_system.rag.retriever import graphrag_query, stale_impact_report

log = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    name = "ResearchAgent"
    role = "research"

    def run(self, question: str = "", **kwargs) -> Any:
        log.info("[ResearchAgent] running query: %s", question or "<stale impact>")
        try:
            if question:
                result = graphrag_query(question)
            else:
                result = stale_impact_report()
            self._mark_idle()
            return result
        except Exception as exc:
            self._mark_error(str(exc))
            raise
