#!/usr/bin/env python3
"""Ingest documents into a vector store."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag_system.config import Settings
from rag_system.ingestion import IngestionPipeline
from rag_system.stores.chroma_store import ChromaVectorStore
from rag_system.stores.pgvector_store import PgVectorStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into a vector store")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "sample_docs",
        help="Directory containing .txt/.md files",
    )
    parser.add_argument(
        "--store",
        choices=["chroma", "pgvector", "both"],
        default="chroma",
        help="Target vector store backend",
    )
    args = parser.parse_args()

    settings = Settings.load()
    stores = []
    if args.store in {"chroma", "both"}:
        stores.append(ChromaVectorStore(settings.chroma, settings.embeddings))
    if args.store in {"pgvector", "both"}:
        stores.append(PgVectorStore(settings.pgvector, settings.embeddings))

    for store in stores:
        pipeline = IngestionPipeline(settings, store)
        result = pipeline.ingest_directory(args.input)
        print(
            f"[{result.store_name}] processed {result.files_processed} files, "
            f"indexed {result.chunks_created} chunks (total={store.count()})"
        )


if __name__ == "__main__":
    main()