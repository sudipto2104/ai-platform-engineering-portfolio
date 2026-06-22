from __future__ import annotations

from rank_bm25 import BM25Okapi

from rag_system.chunking import DocumentChunk
from rag_system.stores.base import RetrievedDocument, VectorStore


class HybridRetriever:
    """Combine dense vector search with sparse BM25 scoring."""

    def __init__(self, store: VectorStore, alpha: float = 0.7):
        self.store = store
        self.alpha = alpha
        self._chunks: list[DocumentChunk] = []
        self._bm25: BM25Okapi | None = None
        self._tokenized_corpus: list[list[str]] = []

    def index(self, chunks: list[DocumentChunk]) -> None:
        self._chunks = chunks
        self._tokenized_corpus = [chunk.text.lower().split() for chunk in chunks]
        self._bm25 = BM25Okapi(self._tokenized_corpus) if self._tokenized_corpus else None

    def search(self, query: str, top_k: int = 5) -> list[RetrievedDocument]:
        dense_results = self.store.search(query, top_k=top_k * 2)
        if not self._bm25 or not self._chunks:
            return dense_results[:top_k]

        sparse_scores = self._bm25.get_scores(query.lower().split())
        sparse_by_key: dict[str, float] = {}
        max_sparse = max(sparse_scores) if len(sparse_scores) else 1.0
        for chunk, score in zip(self._chunks, sparse_scores):
            key = f"{chunk.metadata.get('source')}::{chunk.metadata.get('chunk_index')}"
            sparse_by_key[key] = float(score / max_sparse) if max_sparse else 0.0

        combined: list[RetrievedDocument] = []
        for doc in dense_results:
            key = f"{doc.metadata.get('source')}::{doc.metadata.get('chunk_index')}"
            sparse = sparse_by_key.get(key, 0.0)
            hybrid_score = self.alpha * doc.score + (1 - self.alpha) * sparse
            combined.append(
                RetrievedDocument(
                    text=doc.text,
                    metadata={**doc.metadata, "dense_score": doc.score, "sparse_score": sparse},
                    score=hybrid_score,
                    store=doc.store,
                )
            )

        combined.sort(key=lambda d: d.score, reverse=True)
        return combined[:top_k]