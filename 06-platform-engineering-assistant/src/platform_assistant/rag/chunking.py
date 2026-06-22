from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import tiktoken


@dataclass
class DocumentChunk:
    text: str
    metadata: dict
    token_count: int


class TokenChunker:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._encoder = tiktoken.get_encoding("cl100k_base")

    def chunk_file(self, path: Path) -> list[DocumentChunk]:
        text = path.read_text(encoding="utf-8")
        tokens = self._encoder.encode(text)
        if not tokens:
            return []

        chunks: list[DocumentChunk] = []
        step = self.chunk_size - self.chunk_overlap
        for start in range(0, len(tokens), step):
            window = tokens[start : start + self.chunk_size]
            if not window:
                break
            chunk_text = self._encoder.decode(window)
            chunks.append(
                DocumentChunk(
                    text=chunk_text,
                    metadata={
                        "source": str(path),
                        "filename": path.name,
                        "chunk_index": len(chunks),
                    },
                    token_count=len(window),
                )
            )
            if start + self.chunk_size >= len(tokens):
                break
        return chunks

    def chunk_directory(self, directory: Path) -> list[DocumentChunk]:
        all_chunks: list[DocumentChunk] = []
        for path in sorted(directory.glob("**/*")):
            if path.is_file() and path.suffix in {".txt", ".md"}:
                all_chunks.extend(self.chunk_file(path))
        return all_chunks