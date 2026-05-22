"""Sentence-transformer embeddings with ChromaDB persistence."""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

_model = None
_chroma_client = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        from agent_graph_system.config import cfg
        _model = SentenceTransformer(cfg.embedding.model, trust_remote_code=True)
        log.info("Loaded embedding model: %s", cfg.embedding.model)
    return _model


def _get_collection():
    global _chroma_client, _collection
    if _collection is None:
        import chromadb
        from agent_graph_system.config import cfg
        _chroma_client = chromadb.PersistentClient(path=str(cfg.chroma.persist_dir))
        _collection = _chroma_client.get_or_create_collection(cfg.chroma.collection)
        log.info("ChromaDB collection '%s' ready at %s", cfg.chroma.collection, cfg.chroma.persist_dir)
    return _collection


def embed_text(text: str) -> list[float]:
    return _get_model().encode(text).tolist()


def upsert(doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
    """Embed text and store in ChromaDB, linked to a graph node via doc_id."""
    embedding = embed_text(text)
    _get_collection().upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata or {}],
    )
    log.debug("Upserted embedding for '%s'", doc_id)


def search(query_text: str, n_results: int = 10, where: dict | None = None) -> list[dict[str, Any]]:
    """Semantic search — returns list of {id, document, metadata, distance}."""
    embedding = embed_text(query_text)
    kwargs: dict[str, Any] = {"query_embeddings": [embedding], "n_results": n_results}
    if where:
        kwargs["where"] = where
    results = _get_collection().query(**kwargs)
    return [
        {"id": id_, "document": doc, "metadata": meta, "distance": dist}
        for id_, doc, meta, dist in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def embed_node(node_type: str, node_name: str, description: str, extra_meta: dict | None = None) -> None:
    doc_id = f"{node_type}::{node_name}"
    metadata = {"node_type": node_type, "node_name": node_name, **(extra_meta or {})}
    upsert(doc_id, description, metadata)
