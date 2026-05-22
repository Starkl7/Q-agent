"""Coding agent: parses repos and keeps notebook dependency graph fresh."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agent_graph_system.agents.base_agent import BaseAgent
from agent_graph_system.ingestion.github.graph_writer import ingest_repo

log = logging.getLogger(__name__)


class CodingAgent(BaseAgent):
    name = "CodingAgent"
    role = "coding"

    def run(self, repo_path: str | Path = "", repo_url: str = "", **kwargs) -> Any:
        path = Path(repo_path) if repo_path else Path.cwd()
        log.info("[CodingAgent] scanning repo at %s", path)
        try:
            result = ingest_repo(path, repo_url=repo_url)
            self._mark_idle()
            return result
        except Exception as exc:
            self._mark_error(str(exc))
            raise
