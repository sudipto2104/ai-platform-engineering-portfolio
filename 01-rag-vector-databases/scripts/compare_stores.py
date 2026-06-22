#!/usr/bin/env python3
"""Compare retrieval results between Chroma and pgvector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag_system.config import Settings
from rag_system.stores.chroma_store import ChromaVectorStore
from rag_system.stores.comparison import compare_stores
from rag_system.stores.pgvector_store import PgVectorStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Chroma vs pgvector retrieval")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    settings = Settings.load()
    chroma = ChromaVectorStore(settings.chroma, settings.embeddings)
    pgvector = PgVectorStore(settings.pgvector, settings.embeddings)

    result = compare_stores(chroma, pgvector, args.query, top_k=args.top_k)
    print(result.summary())

    pgvector.close()


if __name__ == "__main__":
    main()