from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from rag_system.chunking import DocumentChunk


@dataclass
class RetrievedDocument:
    text: str
    metadata: dict
    score: float
    store: str

    @property
    def citation(self) -> str:
        source = self.metadata.get("source") or self.metadata.get("filename", "unknown")
        chunk_index = self.metadata.get("chunk_index", "?")
        return f"[{source}#chunk-{chunk_index}]"


class VectorStore(ABC):
    name: str

    @abstractmethod
    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        ...

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[RetrievedDocument]:
        ...

    @abstractmethod
    def count(self) -> int:
        ...