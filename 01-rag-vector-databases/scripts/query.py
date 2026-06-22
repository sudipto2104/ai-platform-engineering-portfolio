#!/usr/bin/env python3
"""Query the RAG pipeline with source citations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag_system.chunking import TokenChunker
from rag_system.config import Settings
from rag_system.rag.pipeline import RAGPipeline
from rag_system.retrieval.hybrid_search import HybridRetriever
from rag_system.stores.chroma_store import ChromaVectorStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the RAG knowledge base")
    parser.add_argument("question", help="Question to ask")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--no-hybrid", action="store_true")
    args = parser.parse_args()

    settings = Settings.load()
    store = ChromaVectorStore(settings.chroma, settings.embeddings)

    pipeline = RAGPipeline(settings, store, use_hybrid=not args.no_hybrid)
    if not args.no_hybrid:
        chunker = TokenChunker(settings.chunking)
        chunks = list(chunker.chunk_directory(PROJECT_ROOT / "data" / "sample_docs"))
        HybridRetriever(store, alpha=settings.retrieval.hybrid_alpha).index(chunks)
        pipeline._retriever.index(chunks)

    response = pipeline.query(args.question, top_k=args.top_k)
    print(response.formatted())


if __name__ == "__main__":
    main()