"""AI Gateway — main entry point for the Platform Engineering Assistant."""

from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app
from pydantic import BaseModel, Field

from platform_assistant.agent.assistant import PlatformAssistant
from platform_assistant.config import Settings
from platform_assistant.observability.logging import log_request_response, setup_logging
from platform_assistant.observability.metrics import gateway_requests_total, record_guardrail
from platform_assistant.security.guardrails import validate_input
from platform_assistant.security.vault import VaultClient

settings = Settings.load()
logger = setup_logging(settings.log_level)
vault = VaultClient(settings.vault_addr, settings.vault_token, settings.vault_secret_path)
_assistant: PlatformAssistant | None = None


def get_assistant() -> PlatformAssistant:
    global _assistant
    if _assistant is None:
        _assistant = PlatformAssistant(settings)
    return _assistant

app = FastAPI(
    title="Platform Engineering Assistant",
    description="AI Infrastructure Capstone — RAG + Agents + Observability + Vault",
    version="1.0.0",
)
app.mount("/metrics", make_asgi_app())


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    citations: list[str]
    latency_ms: float


@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "model": settings.ollama_model,
        "chunks_indexed": get_assistant().rag_store.count(),
        "vault_mode": "local" if vault._use_local_fallback() else "remote",
    }


@app.get("/ready")
async def ready() -> dict:
    if get_assistant().rag_store.count() == 0:
        raise HTTPException(status_code=503, detail="RAG index not populated")
    return {"status": "ready"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())
    validation = validate_input(request.question)
    if not validation.allowed:
        record_guardrail("input_validation", "blocked")
        gateway_requests_total.labels(endpoint="/chat", status="blocked").inc()
        raise HTTPException(status_code=400, detail=validation.reason)

    _ = vault.read_secrets()
    start = time.perf_counter()
    try:
        result = get_assistant().chat(request.question, session_id=session_id)
        status = "success"
    except Exception as exc:
        gateway_requests_total.labels(endpoint="/chat", status="error").inc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    gateway_requests_total.labels(endpoint="/chat", status=status).inc()
    latency_ms = (time.perf_counter() - start) * 1000

    log_request_response(
        logger,
        session_id=session_id,
        question=request.question,
        answer=result.answer,
        model=settings.ollama_model,
        citations=result.citations,
        latency_ms=latency_ms,
    )

    return ChatResponse(
        answer=result.answer,
        session_id=session_id,
        citations=result.citations,
        latency_ms=round(latency_ms, 2),
    )


def main() -> None:
    import uvicorn

    uvicorn.run(
        "platform_assistant.gateway.app:app",
        host="0.0.0.0",
        port=settings.gateway_port,
        reload=False,
    )


if __name__ == "__main__":
    main()