"""Write parsed GitHub repo data into the Neo4j knowledge graph."""

from __future__ import annotations

import logging
from pathlib import Path

from agent_graph_system.graph.neo4j import graph_models as gm
from agent_graph_system.ingestion.github.parser import scan_repo

log = logging.getLogger(__name__)


def ingest_repo(repo_root: Path, repo_url: str = "") -> dict:
    scan = scan_repo(repo_root)
    repo_name = scan["repo"]

    gm.upsert_repository(repo_name, url=repo_url or str(repo_root), branch="main")
    log.info("Ingesting repo '%s' — %d notebooks found", repo_name, scan["total"])

    for nb in scan["notebooks"]:
        gm.upsert_notebook(
            name=nb["name"],
            path=nb["path"],
            notebook_type=nb["notebook_type"],
        )
        gm.repository_contains_notebook(repo_name, nb["name"])

        for ds_source in nb["datasets"]:
            ds_name = f"{ds_source}_Data"
            gm.upsert_dataset(ds_name, source=ds_source)
            gm.notebook_uses_dataset(nb["name"], ds_name)
            log.debug("  %s -[USES]-> %s", nb["name"], ds_name)

    return scan
