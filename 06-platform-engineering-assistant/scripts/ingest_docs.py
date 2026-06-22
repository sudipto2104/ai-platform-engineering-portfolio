#!/usr/bin/env python3
"""Ingest Kubernetes documentation into ChromaDB."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from platform_assistant.config import Settings
from platform_assistant.rag.store import RAGStore


def main() -> None:
    settings = Settings.load()
    store = RAGStore(settings)
    docs_dir = PROJECT_ROOT / "data" / "docs"
    count = store.ingest_directory(docs_dir)
    print(f"Ingested {count} chunks from {docs_dir} (total={store.count()})")


if __name__ == "__main__":
    main()