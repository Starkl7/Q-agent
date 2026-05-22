"""Central configuration — read from environment, fall back to defaults."""

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).parent


@dataclass
class Neo4jConfig:
    uri: str = field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    user: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "password"))
    database: str = field(default_factory=lambda: os.getenv("NEO4J_DATABASE", "neo4j"))


@dataclass
class ChromaConfig:
    host: str = field(default_factory=lambda: os.getenv("CHROMA_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("CHROMA_PORT", "8000")))
    collection: str = field(default_factory=lambda: os.getenv("CHROMA_COLLECTION", "agent_graph"))
    persist_dir: Path = field(default_factory=lambda: Path(os.getenv("CHROMA_PERSIST_DIR", str(ROOT / ".chroma"))))


@dataclass
class EmbeddingConfig:
    model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1"))
    batch_size: int = 64


@dataclass
class GitHubConfig:
    token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    webhook_secret: str = field(default_factory=lambda: os.getenv("GITHUB_WEBHOOK_SECRET", ""))
    repos: list[str] = field(default_factory=lambda: os.getenv("GITHUB_REPOS", "wolfpackofone/q-agent").split(","))


@dataclass
class APIConfig:
    host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8080")))
    reload: bool = field(default_factory=lambda: os.getenv("API_RELOAD", "true").lower() == "true")


@dataclass
class Config:
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    chroma: ChromaConfig = field(default_factory=ChromaConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    github: GitHubConfig = field(default_factory=GitHubConfig)
    api: APIConfig = field(default_factory=APIConfig)
    ontology_dir: Path = ROOT / "ontology" / "schema"
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


cfg = Config()
