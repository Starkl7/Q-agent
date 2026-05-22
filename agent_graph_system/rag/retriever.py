"""GraphRAG retriever: semantic search + graph traversal combined."""

from __future__ import annotations

import logging
from typing import Any

from agent_graph_system.embeddings.embedder import search
from agent_graph_system.graph.backend import query

log = logging.getLogger(__name__)


def graphrag_query(question: str, n_semantic: int = 5, graph_hops: int = 2) -> dict[str, Any]:
    """
    Two-phase retrieval:
      1. Semantic: find closest nodes by embedding similarity.
      2. Graph: traverse the ontology from those seed nodes to gather context.
    Returns a dict with 'semantic_hits' and 'graph_context'.
    """
    semantic_hits = search(question, n_results=n_semantic)

    seed_nodes: list[tuple[str, str]] = []
    for hit in semantic_hits:
        meta = hit.get("metadata", {})
        node_type = meta.get("node_type", "")
        node_name = meta.get("node_name", "")
        if node_type and node_name:
            seed_nodes.append((node_type, node_name))

    graph_context: list[dict] = []
    for node_type, node_name in seed_nodes:
        name_key = "ticker" if node_type == "Security" else "run_id" if node_type == "Backtest" else "name"
        rows = query(
            f"""
            MATCH path = (seed:{node_type} {{{name_key}: $name}})-[*1..{graph_hops}]-(neighbour)
            RETURN DISTINCT
                labels(seed)[0]     AS seed_type,
                seed.name           AS seed_name,
                type(relationships(path)[-1]) AS rel,
                labels(neighbour)[0] AS neighbour_type,
                neighbour.name      AS neighbour_name,
                neighbour.status    AS neighbour_status
            LIMIT 50
            """,
            name=node_name,
        )
        graph_context.extend(rows)

    return {
        "question": question,
        "semantic_hits": semantic_hits,
        "graph_context": graph_context,
    }


def stale_impact_report() -> dict[str, Any]:
    """Identify stale datasets and list every downstream entity they affect."""
    stale = query("MATCH (d:Dataset) WHERE d.status = 'stale' RETURN d.name AS name, d.source AS source")
    impact: dict[str, list] = {}
    for ds in stale:
        ds_name = ds["name"]
        rows = query(
            """
            MATCH (e)-[:USES|DEPENDS_ON|FEEDS]->(d:Dataset {name: $name})
            RETURN labels(e)[0] AS type, e.name AS name, e.status AS status
            """,
            name=ds_name,
        )
        impact[ds_name] = rows
    return {"stale_datasets": stale, "downstream_impact": impact}


def strategy_readiness(strategy_name: str) -> dict[str, Any]:
    """Check if a strategy's full dependency chain is healthy."""
    deps = query(
        """
        MATCH (s:Strategy {name: $name})-[:USES|DEPENDS_ON]->(d)
        RETURN labels(d)[0] AS dep_type, d.name AS dep_name, d.status AS status
        """,
        name=strategy_name,
    )
    is_ready = all(d.get("status") in (None, "fresh", "active") for d in deps)
    return {"strategy": strategy_name, "dependencies": deps, "ready": is_ready}
