from __future__ import annotations

import time

from prometheus_client import Counter, Histogram

gateway_requests_total = Counter(
    "gateway_requests_total",
    "Total gateway requests",
    ["endpoint", "status"],
)

llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["model", "status", "request_type"],
)

llm_tokens_total = Counter(
    "llm_tokens_total",
    "Total tokens processed",
    ["model", "token_type"],
)

llm_latency_seconds = Histogram(
    "llm_latency_seconds",
    "LLM latency by phase",
    ["model", "phase"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30],
)

llm_cost_dollars_total = Counter(
    "llm_cost_dollars_total",
    "Estimated LLM cost",
    ["model", "feature"],
)

guardrail_triggers_total = Counter(
    "guardrail_triggers_total",
    "Guardrail triggers",
    ["guardrail_type", "action"],
)

rag_retrievals_total = Counter(
    "rag_retrievals_total",
    "RAG retrieval operations",
    ["status"],
)


class track_request:
    def __init__(self, model: str, request_type: str = "chat", feature: str = "platform_assistant"):
        self.model = model
        self.request_type = request_type
        self.feature = feature
        self._start: float | None = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._start is None:
            return
        elapsed = time.perf_counter() - self._start
        status = "success" if exc_type is None else "error"
        llm_requests_total.labels(model=self.model, status=status, request_type=self.request_type).inc()
        llm_latency_seconds.labels(model=self.model, phase="total").observe(elapsed)


def record_tokens(model: str, input_tokens: int, output_tokens: int) -> None:
    llm_tokens_total.labels(model=model, token_type="input").inc(input_tokens)
    llm_tokens_total.labels(model=model, token_type="output").inc(output_tokens)


def estimate_ollama_cost(model: str, total_tokens: int, feature: str = "platform_assistant") -> float:
    cost = total_tokens * 0.000001
    llm_cost_dollars_total.labels(model=model, feature=feature).inc(cost)
    return cost


def record_guardrail(guardrail_type: str, action: str) -> None:
    guardrail_triggers_total.labels(guardrail_type=guardrail_type, action=action).inc()