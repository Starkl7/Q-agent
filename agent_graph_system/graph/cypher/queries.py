"""Named Cypher queries for common GraphRAG retrieval patterns."""

from agent_graph_system.graph.backend import query


def notebooks_using_wrds() -> list[dict]:
    return query(
        """
        MATCH (n:Notebook)-[:USES]->(d:Dataset)
        WHERE d.source = 'WRDS'
        RETURN n.name AS notebook, n.path AS path, d.name AS dataset, d.status AS data_status
        ORDER BY n.name
        """
    )


def stale_strategy_dependencies() -> list[dict]:
    return query(
        """
        MATCH (s:Strategy)-[:USES|DEPENDS_ON]->(d:Dataset)
        WHERE d.status = 'stale'
        RETURN s.name AS strategy, s.status AS strategy_status, d.name AS stale_dataset, d.last_updated AS last_updated
        ORDER BY d.last_updated
        """
    )


def backtest_lineage(strategy_name: str) -> list[dict]:
    return query(
        """
        MATCH (s:Strategy {name: $name})<-[:USED_BY]-(d:Dataset)
        OPTIONAL MATCH (s)<-[:GENERATES]-(n:Notebook)-[:GENERATES]->(b:Backtest)
        RETURN s.name AS strategy, d.name AS dataset, n.name AS notebook, b.run_id AS backtest_id,
               b.sharpe AS sharpe, b.cagr AS cagr
        """,
        name=strategy_name,
    )


def active_deployments() -> list[dict]:
    return query(
        """
        MATCH (s:Strategy)-[r:DEPLOYS_TO]->(a:API)
        WHERE r.environment IN ['live', 'paper']
        RETURN s.name AS strategy, a.name AS broker, r.environment AS env, r.deployed_at AS deployed_at
        ORDER BY r.deployed_at DESC
        """
    )


def pipeline_health() -> list[dict]:
    return query(
        """
        MATCH (p:Pipeline)
        OPTIONAL MATCH (p)-[:PRODUCES]->(d:Dataset)
        RETURN p.name AS pipeline, p.status AS status, p.last_run AS last_run,
               collect(d.name) AS output_datasets
        ORDER BY p.last_run
        """
    )


def dataset_dependency_graph(dataset_name: str) -> list[dict]:
    """All notebooks and strategies that depend on a given dataset."""
    return query(
        """
        MATCH (e)-[:USES|DEPENDS_ON]->(d:Dataset {name: $name})
        RETURN labels(e)[0] AS entity_type, e.name AS entity, e.status AS status
        ORDER BY entity_type, e.name
        """,
        name=dataset_name,
    )


def full_strategy_context(strategy_name: str) -> list[dict]:
    """GraphRAG: retrieve everything connected to a strategy within 2 hops."""
    return query(
        """
        MATCH path = (s:Strategy {name: $name})-[*1..2]-(connected)
        RETURN DISTINCT
            labels(connected)[0] AS node_type,
            connected.name AS name,
            type(relationships(path)[-1]) AS via_relationship
        ORDER BY node_type, name
        """,
        name=strategy_name,
    )


def agent_task_graph() -> list[dict]:
    """Which agent monitors which pipelines and datasets."""
    return query(
        """
        MATCH (a:Agent)-[r:MONITORS]->(target)
        RETURN a.name AS agent, a.role AS role, labels(target)[0] AS watching_type,
               target.name AS watching, target.status AS target_status
        ORDER BY a.name
        """
    )


def create_indexes() -> None:
    from agent_graph_system.graph.backend import create_indexes as _ci
    _ci()
