from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import tiktoken

from rag_system.config import ChunkingConfig


@dataclass
class DocumentChunk:
    text: str
    metadata: dict
    token_count: int


class TokenChunker:
    """Split documents into overlapping token-based chunks."""

    def __init__(self, config: ChunkingConfig):
        self.config = config
        self._encoder = tiktoken.get_encoding(config.encoding)

    def count_tokens(self, text: str) -> int:
        return len(self._encoder.encode(text))

    def chunk_text(self, text: str, metadata: dict | None = None) -> list[DocumentChunk]:
        metadata = metadata or {}
        tokens = self._encoder.encode(text)
        if not tokens:
            return []

        chunks: list[DocumentChunk] = []
        step = self.config.chunk_size - self.config.chunk_overlap
        if step <= 0:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        for start in range(0, len(tokens), step):
            window = tokens[start : start + self.config.chunk_size]
            if not window:
                break
            chunk_text = self._encoder.decode(window)
            chunk_meta = {
                **metadata,
                "chunk_index": len(chunks),
                "token_count": len(window),
                "token_start": start,
            }
            chunks.append(
                DocumentChunk(text=chunk_text, metadata=chunk_meta, token_count=len(window))
            )
            if start + self.config.chunk_size >= len(tokens):
                break

        return chunks

    def chunk_file(self, path: Path) -> list[DocumentChunk]:
        text = path.read_text(encoding="utf-8")
        metadata = {
            "source": str(path),
            "filename": path.name,
            "doc_type": path.suffix.lstrip(".") or "txt",
        }
        return self.chunk_text(text, metadata)

    def chunk_directory(self, directory: Path, pattern: str = "**/*") -> Iterator[DocumentChunk]:
        for path in sorted(directory.glob(pattern)):
            if path.is_file() and path.suffix in {".txt", ".md"}:
                yield from self.chunk_file(path)