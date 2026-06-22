"""Lightweight inference server for Kubernetes resource management demos."""

from __future__ import annotations

import asyncio
import hashlib
import os
import time
from typing import Any

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

MODEL_MEMORY_MB = int(os.getenv("MODEL_MEMORY_MB", "256"))
INFERENCE_LATENCY_MS = int(os.getenv("INFERENCE_LATENCY_MS", "120"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    _warm_model()
    yield


app = FastAPI(title="ML Inference Server", version="1.0.0", lifespan=lifespan)

_model_cache: list[bytearray] = []
_request_count = 0
_total_latency_ms = 0.0


class PredictRequest(BaseModel):
    input_text: str = Field(..., min_length=1)
    max_tokens: int = Field(default=64, ge=1, le=512)


class PredictResponse(BaseModel):
    prediction: str
    latency_ms: float
    model_memory_mb: int


def _warm_model() -> None:
    """Allocate memory to simulate model weights loaded at startup."""
    global _model_cache
    if not _model_cache:
        _model_cache.append(bytearray(MODEL_MEMORY_MB * 1024 * 1024))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    avg_latency = _total_latency_ms / _request_count if _request_count else 0.0
    return {
        "requests_total": _request_count,
        "avg_latency_ms": round(avg_latency, 2),
        "model_memory_mb": MODEL_MEMORY_MB,
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    global _request_count, _total_latency_ms

    start = time.perf_counter()
    await asyncio.sleep(INFERENCE_LATENCY_MS / 1000)

    digest = hashlib.sha256(request.input_text.encode()).hexdigest()[:16]
    prediction = f"label-{digest}-tokens-{request.max_tokens}"

    latency_ms = (time.perf_counter() - start) * 1000
    _request_count += 1
    _total_latency_ms += latency_ms

    return PredictResponse(
        prediction=prediction,
        latency_ms=round(latency_ms, 2),
        model_memory_mb=MODEL_MEMORY_MB,
    )