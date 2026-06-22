"""Retrieval API for the RAG subsystem."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from platform_assistant.config import Settings
from platform_assistant.rag.store import RAGStore

settings = Settings.load()
store = RAGStore(settings)

app = FastAPI(title="Platform Assistant RAG API", version="1.0.0")


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrieveResponse(BaseModel):
    query: str
    results: list[dict]
    total_chunks: int


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "chunks_indexed": store.count()}


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    docs = store.search(request.query, top_k=request.top_k)
    return RetrieveResponse(
        query=request.query,
        results=[
            {
                "text": doc.text,
                "citation": doc.citation,
                "score": doc.score,
                "metadata": doc.metadata,
            }
            for doc in docs
        ],
        total_chunks=store.count(),
    )