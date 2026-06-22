from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from platform_assistant.config import Settings
from platform_assistant.rag.chunking import DocumentChunk, TokenChunker


@dataclass
class RetrievedDoc:
    text: str
    metadata: dict
    score: float

    @property
    def citation(self) -> str:
        source = self.metadata.get("filename", "unknown")
        chunk = self.metadata.get("chunk_index", "?")
        return f"[{source}#chunk-{chunk}]"


class RAGStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=self._embeddings,
            persist_directory=str(persist_dir),
        )
        self._chunker = TokenChunker(settings.chunk_size, settings.chunk_overlap)

    def ingest_directory(self, directory: Path) -> int:
        chunks = self._chunker.chunk_directory(directory)
        return self.add_chunks(chunks)

    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0
        docs = [Document(page_content=c.text, metadata=c.metadata) for c in chunks]
        ids = [str(uuid4()) for _ in chunks]
        self._store.add_documents(documents=docs, ids=ids)
        return len(chunks)

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedDoc]:
        k = top_k or self.settings.retrieval_top_k
        results = self._store.similarity_search_with_score(query, k=k)
        return [
            RetrievedDoc(
                text=doc.page_content,
                metadata=doc.metadata,
                score=float(1.0 / (1.0 + distance)),
            )
            for doc, distance in results
        ]

    def count(self) -> int:
        return self._store._collection.count()