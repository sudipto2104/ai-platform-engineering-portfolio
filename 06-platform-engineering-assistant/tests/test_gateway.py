from pathlib import Path

from fastapi.testclient import TestClient

import platform_assistant.gateway.app as gateway_module
from platform_assistant.config import Settings
from platform_assistant.rag.store import RAGStore

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_rag(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    settings = Settings.load()
    store = RAGStore(settings)
    store.ingest_directory(PROJECT_ROOT / "data" / "docs")

    class _StubAssistant:
        def __init__(self):
            self.rag_store = store

        def chat(self, question: str, session_id: str = "default"):
            validation = gateway_module.validate_input(question)
            if not validation.allowed:
                from platform_assistant.agent.assistant import AssistantResponse

                return AssistantResponse(
                    answer=f"I cannot process this request: {validation.reason}",
                    session_id=session_id,
                )
            from platform_assistant.agent.assistant import AssistantResponse

            return AssistantResponse(
                answer="Stub response for testing.",
                session_id=session_id,
            )

    gateway_module._assistant = _StubAssistant()


def test_health_endpoint(tmp_path, monkeypatch) -> None:
    _bootstrap_rag(tmp_path, monkeypatch)
    client = TestClient(gateway_module.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_blocks_off_topic_chat(tmp_path, monkeypatch) -> None:
    _bootstrap_rag(tmp_path, monkeypatch)
    client = TestClient(gateway_module.app)
    response = client.post("/chat", json={"question": "Tell me celebrity gossip recipes"})
    assert response.status_code == 400