from __future__ import annotations

from dataclasses import dataclass

from rag_system.config import Settings
from rag_system.retrieval.hybrid_search import HybridRetriever
from rag_system.stores.base import RetrievedDocument, VectorStore


@dataclass
class RAGResponse:
    query: str
    answer: str
    citations: list[str]
    sources: list[RetrievedDocument]

    def formatted(self) -> str:
        citation_block = "\n".join(f"  - {c}" for c in self.citations)
        return f"{self.answer}\n\nSources:\n{citation_block}"


class RAGPipeline:
    """Retrieve context and generate cited answers from indexed documents."""

    def __init__(self, settings: Settings, store: VectorStore, use_hybrid: bool = True):
        self.settings = settings
        self.store = store
        self.use_hybrid = use_hybrid
        self._retriever = HybridRetriever(store, alpha=settings.retrieval.hybrid_alpha)

    def query(self, question: str, top_k: int | None = None) -> RAGResponse:
        k = top_k or self.settings.retrieval.top_k
        if self.use_hybrid:
            results = self._retriever.search(question, top_k=k)
        else:
            results = self.store.search(question, top_k=k)

        if not results:
            return RAGResponse(
                query=question,
                answer="No relevant documents found in the knowledge base.",
                citations=[],
                sources=[],
            )

        context_blocks = []
        citations = []
        for i, doc in enumerate(results, start=1):
            citation = doc.citation
            citations.append(citation)
            context_blocks.append(f"[{i}] {doc.text}\nSource: {citation}")

        context = "\n\n".join(context_blocks)
        answer = self._synthesize_answer(question, context, citations)
        return RAGResponse(
            query=question,
            answer=answer,
            citations=citations,
            sources=results,
        )

    def _synthesize_answer(self, question: str, context: str, citations: list[str]) -> str:
        """Template-based synthesis for offline/demo use without an LLM API key."""
        intro = (
            f"Based on {len(citations)} retrieved document chunk(s), "
            f"here is a summary for: {question}"
        )
        excerpt = context[:1200].strip()
        if len(context) > 1200:
            excerpt += "..."
        return f"{intro}\n\n{excerpt}"