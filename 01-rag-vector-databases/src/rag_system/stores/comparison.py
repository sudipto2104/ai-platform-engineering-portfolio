from __future__ import annotations

from dataclasses import dataclass

from rag_system.stores.base import RetrievedDocument, VectorStore


@dataclass
class ComparisonResult:
    query: str
    chroma_results: list[RetrievedDocument]
    pgvector_results: list[RetrievedDocument]
    overlap_count: int
    chroma_latency_ms: float
    pgvector_latency_ms: float

    def summary(self) -> str:
        lines = [
            f"Query: {self.query}",
            f"Chroma latency: {self.chroma_latency_ms:.1f}ms | pgvector latency: {self.pgvector_latency_ms:.1f}ms",
            f"Result overlap (by source+chunk): {self.overlap_count}",
            "",
            "Top Chroma hits:",
        ]
        for doc in self.chroma_results[:3]:
            lines.append(f"  {doc.citation} score={doc.score:.3f}")
        lines.append("")
        lines.append("Top pgvector hits:")
        for doc in self.pgvector_results[:3]:
            lines.append(f"  {doc.citation} score={doc.score:.3f}")
        return "\n".join(lines)


def _doc_key(doc: RetrievedDocument) -> str:
    source = doc.metadata.get("source", doc.metadata.get("filename", ""))
    chunk_index = doc.metadata.get("chunk_index", "")
    return f"{source}::{chunk_index}"


def compare_stores(
    chroma: VectorStore,
    pgvector: VectorStore,
    query: str,
    top_k: int = 5,
) -> ComparisonResult:
    import time

    start = time.perf_counter()
    chroma_results = chroma.search(query, top_k=top_k)
    chroma_latency = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    pgvector_results = pgvector.search(query, top_k=top_k)
    pgvector_latency = (time.perf_counter() - start) * 1000

    chroma_keys = {_doc_key(doc) for doc in chroma_results}
    pgvector_keys = {_doc_key(doc) for doc in pgvector_results}
    overlap = len(chroma_keys & pgvector_keys)

    return ComparisonResult(
        query=query,
        chroma_results=chroma_results,
        pgvector_results=pgvector_results,
        overlap_count=overlap,
        chroma_latency_ms=chroma_latency,
        pgvector_latency_ms=pgvector_latency,
    )