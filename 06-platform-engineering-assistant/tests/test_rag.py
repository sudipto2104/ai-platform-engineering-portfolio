from pathlib import Path

from platform_assistant.config import Settings
from platform_assistant.rag.store import RAGStore

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_ingest_and_search(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    settings = Settings.load()
    store = RAGStore(settings)
    count = store.ingest_directory(PROJECT_ROOT / "data" / "docs")
    assert count > 0
    results = store.search("CrashLoopBackOff troubleshooting")
    assert results
    assert any("CrashLoopBackOff" in doc.text for doc in results)