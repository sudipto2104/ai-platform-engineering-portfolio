from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rag_system.chunking import DocumentChunk, TokenChunker
from rag_system.config import Settings
from rag_system.stores.base import VectorStore


@dataclass
class IngestionResult:
    files_processed: int
    chunks_created: int
    store_name: str


class IngestionPipeline:
    def __init__(self, settings: Settings, store: VectorStore):
        self.settings = settings
        self.store = store
        self.chunker = TokenChunker(settings.chunking)

    def ingest_directory(self, directory: Path) -> IngestionResult:
        all_chunks: list[DocumentChunk] = []
        files_processed = 0

        for path in sorted(directory.glob("**/*")):
            if path.is_file() and path.suffix in {".txt", ".md"}:
                all_chunks.extend(self.chunker.chunk_file(path))
                files_processed += 1

        added = self.store.add_chunks(all_chunks)
        return IngestionResult(
            files_processed=files_processed,
            chunks_created=added,
            store_name=self.store.name,
        )

    def ingest_text(self, text: str, metadata: dict | None = None) -> IngestionResult:
        chunks = self.chunker.chunk_text(text, metadata or {})
        added = self.store.add_chunks(chunks)
        return IngestionResult(
            files_processed=1,
            chunks_created=added,
            store_name=self.store.name,
        )