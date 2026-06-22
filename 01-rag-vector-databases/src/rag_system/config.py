from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open() as f:
        return yaml.safe_load(f) or {}


@dataclass
class ChunkingConfig:
    chunk_size: int = 600
    chunk_overlap: int = 80
    encoding: str = "cl100k_base"


@dataclass
class EmbeddingsConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"


@dataclass
class RetrievalConfig:
    top_k: int = 5
    hybrid_alpha: float = 0.7


@dataclass
class ChromaConfig:
    persist_directory: str = "./data/chroma"
    collection_name: str = "platform_docs"
    host: str = "localhost"
    port: int = 8000


@dataclass
class PgVectorConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "rag"
    user: str = "rag"
    password: str = "rag123"
    table_name: str = "document_embeddings"


@dataclass
class Settings:
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    embeddings: EmbeddingsConfig = field(default_factory=EmbeddingsConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    chroma: ChromaConfig = field(default_factory=ChromaConfig)
    pgvector: PgVectorConfig = field(default_factory=PgVectorConfig)

    @classmethod
    def load(cls, config_path: Path | None = None) -> Settings:
        raw = _load_yaml(config_path or DEFAULT_CONFIG_PATH)
        chunking = ChunkingConfig(**raw.get("chunking", {}))
        embeddings = EmbeddingsConfig(**raw.get("embeddings", {}))
        retrieval = RetrievalConfig(**raw.get("retrieval", {}))
        chroma = ChromaConfig(**raw.get("stores", {}).get("chroma", {}))
        pgvector = PgVectorConfig(**raw.get("stores", {}).get("pgvector", {}))

        chunking.chunk_size = int(os.getenv("CHUNK_SIZE", chunking.chunk_size))
        chunking.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", chunking.chunk_overlap))
        embeddings.model_name = os.getenv("EMBEDDING_MODEL", embeddings.model_name)
        chroma.persist_directory = os.getenv("CHROMA_PERSIST_DIR", chroma.persist_directory)
        chroma.collection_name = os.getenv("COLLECTION_NAME", chroma.collection_name)
        chroma.host = os.getenv("CHROMA_HOST", chroma.host)
        chroma.port = int(os.getenv("CHROMA_PORT", chroma.port))
        pgvector.host = os.getenv("PGVECTOR_HOST", pgvector.host)
        pgvector.port = int(os.getenv("PGVECTOR_PORT", pgvector.port))
        pgvector.database = os.getenv("PGVECTOR_DB", pgvector.database)
        pgvector.user = os.getenv("PGVECTOR_USER", pgvector.user)
        pgvector.password = os.getenv("PGVECTOR_PASSWORD", pgvector.password)

        return cls(
            chunking=chunking,
            embeddings=embeddings,
            retrieval=retrieval,
            chroma=chroma,
            pgvector=pgvector,
        )