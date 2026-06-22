import sys
from pathlib import Path
from unittest.mock import MagicMock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag_system.chunking import DocumentChunk
from rag_system.retrieval.hybrid_search import HybridRetriever
from rag_system.stores.base import RetrievedDocument


def test_hybrid_search_combines_scores() -> None:
    store = MagicMock()
    store.search.return_value = [
        RetrievedDocument(
            text="RAG uses vector databases",
            metadata={"source": "doc.txt", "chunk_index": 0},
            score=0.8,
            store="chroma",
        )
    ]

    retriever = HybridRetriever(store, alpha=0.7)
    retriever.index(
        [
            DocumentChunk(
                text="RAG uses vector databases for retrieval",
                metadata={"source": "doc.txt", "chunk_index": 0},
                token_count=10,
            )
        ]
    )

    results = retriever.search("vector databases", top_k=1)
    assert results
    assert results[0].score > 0
    assert "dense_score" in results[0].metadata