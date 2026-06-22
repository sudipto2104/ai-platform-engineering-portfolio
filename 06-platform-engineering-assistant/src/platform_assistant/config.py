from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Settings:
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_persist_dir: str = "./data/chroma"
    collection_name: str = "k8s_docs"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vault_addr: str = "http://localhost:8200"
    vault_token: str = ""
    vault_secret_path: str = "secret/data/platform-assistant"
    gateway_port: int = 8080
    metrics_port: int = 8000
    k8s_dry_run: bool = True
    chunk_size: int = 600
    chunk_overlap: int = 80
    retrieval_top_k: int = 5
    log_level: str = "INFO"

    @classmethod
    def load(cls) -> Settings:
        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
            chroma_host=os.getenv("CHROMA_HOST", "localhost"),
            chroma_port=int(os.getenv("CHROMA_PORT", "8000")),
            chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./data/chroma"),
            collection_name=os.getenv("COLLECTION_NAME", "k8s_docs"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            vault_addr=os.getenv("VAULT_ADDR", "http://localhost:8200"),
            vault_token=os.getenv("VAULT_TOKEN", ""),
            vault_secret_path=os.getenv("VAULT_SECRET_PATH", "secret/data/platform-assistant"),
            gateway_port=int(os.getenv("GATEWAY_PORT", "8080")),
            metrics_port=int(os.getenv("METRICS_PORT", "8000")),
            k8s_dry_run=os.getenv("K8S_DRY_RUN", "true").lower() == "true",
            chunk_size=int(os.getenv("CHUNK_SIZE", "600")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "80")),
            retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "5")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )