import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag_system.chunking import TokenChunker
from rag_system.config import ChunkingConfig


@pytest.fixture
def chunker() -> TokenChunker:
    return TokenChunker(ChunkingConfig(chunk_size=600, chunk_overlap=80))


def test_chunk_text_respects_token_limits(chunker: TokenChunker) -> None:
    text = "word " * 2000
    chunks = chunker.chunk_text(text, {"source": "test.txt"})
    assert chunks
    for chunk in chunks:
        assert chunk.token_count <= 600
        assert chunk.metadata["chunk_index"] >= 0


def test_chunk_overlap_produces_multiple_chunks(chunker: TokenChunker) -> None:
    text = "kubernetes pod service deployment " * 500
    chunks = chunker.chunk_text(text)
    assert len(chunks) > 1


def test_chunk_file_reads_sample_doc(chunker: TokenChunker) -> None:
    path = PROJECT_ROOT / "data" / "sample_docs" / "rag_architecture.txt"
    chunks = chunker.chunk_file(path)
    assert chunks
    assert chunks[0].metadata["filename"] == "rag_architecture.txt"