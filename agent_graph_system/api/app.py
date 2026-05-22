"""FastAPI application — REST interface to the graph and agents."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from agent_graph_system.graph.cypher import queries as cq
from agent_graph_system.graph.backend import graph_stats
from agent_graph_system.rag.retriever import graphrag_query, stale_impact_report, strategy_readiness

log = logging.getLogger(__name__)
app = FastAPI(title="Agent Graph System", version="0.1.0")


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, Any]:
    import os
    backend = os.getenv("GRAPH_BACKEND", "local")
    stats = graph_stats()
    return {"status": "ok", "backend": backend, "graph": stats}


# ---------------------------------------------------------------------------
# Graph queries
# ---------------------------------------------------------------------------

@app.get("/graph/notebooks/wrds")
def notebooks_using_wrds() -> list[dict]:
    return cq.notebooks_using_wrds()


@app.get("/graph/strategies/stale-deps")
def stale_strategy_deps() -> list[dict]:
    return cq.stale_strategy_dependencies()


@app.get("/graph/strategies/{name}/lineage")
def strategy_lineage(name: str) -> list[dict]:
    return cq.backtest_lineage(name)


@app.get("/graph/strategies/{name}/context")
def strategy_context(name: str) -> list[dict]:
    return cq.full_strategy_context(name)


@app.get("/graph/deployments")
def active_deployments() -> list[dict]:
    return cq.active_deployments()


@app.get("/graph/pipelines/health")
def pipeline_health() -> list[dict]:
    return cq.pipeline_health()


@app.get("/graph/datasets/{name}/dependents")
def dataset_dependents(name: str) -> list[dict]:
    return cq.dataset_dependency_graph(name)


@app.get("/graph/agents")
def agent_task_graph() -> list[dict]:
    return cq.agent_task_graph()


# ---------------------------------------------------------------------------
# GraphRAG
# ---------------------------------------------------------------------------

class RAGRequest(BaseModel):
    question: str
    n_results: int = 5


@app.post("/rag/query")
def rag_query(req: RAGRequest) -> dict[str, Any]:
    return graphrag_query(req.question, n_semantic=req.n_results)


@app.get("/rag/stale-impact")
def rag_stale_impact() -> dict[str, Any]:
    return stale_impact_report()


@app.get("/rag/strategy-readiness/{name}")
def rag_strategy_readiness(name: str) -> dict[str, Any]:
    return strategy_readiness(name)


# ---------------------------------------------------------------------------
# Agent triggers
# ---------------------------------------------------------------------------

@app.post("/agents/coding/ingest")
def trigger_coding_agent(repo_path: str = Query(...), repo_url: str = Query("")) -> dict[str, Any]:
    from agent_graph_system.agents.coding_agent import CodingAgent
    return CodingAgent().run(repo_path=repo_path, repo_url=repo_url)


@app.post("/agents/monitoring/run")
def trigger_monitoring_agent() -> dict[str, Any]:
    from agent_graph_system.agents.monitoring_agent import MonitoringAgent
    return MonitoringAgent().run()


@app.post("/agents/orchestration/run")
def trigger_orchestration_agent() -> dict[str, Any]:
    from agent_graph_system.agents.orchestration_agent import OrchestrationAgent
    return OrchestrationAgent().run()
