from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_core.documents import Document

from rag_system.chunking import DocumentChunk
from rag_system.config import ChromaConfig
from rag_system.embeddings import create_embeddings
from rag_system.stores.base import RetrievedDocument, VectorStore


class ChromaVectorStore(VectorStore):
    name = "chroma"

    def __init__(self, config: ChromaConfig, embedding_config):
        self.config = config
        self._embeddings = create_embeddings(embedding_config)
        persist_dir = Path(config.persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self._store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self._embeddings,
            persist_directory=str(persist_dir),
        )

    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0

        documents = [
            Document(page_content=chunk.text, metadata=chunk.metadata)
            for chunk in chunks
        ]
        ids = [str(uuid4()) for _ in chunks]
        self._store.add_documents(documents=documents, ids=ids)
        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list[RetrievedDocument]:
        results = self._store.similarity_search_with_score(query, k=top_k)
        return [
            RetrievedDocument(
                text=doc.page_content,
                metadata=doc.metadata,
                score=float(1.0 / (1.0 + distance)),
                store=self.name,
            )
            for doc, distance in results
        ]

    def count(self) -> int:
        return self._store._collection.count()