"""Production observability layer for LLM-powered applications."""

from __future__ import annotations

import time
from typing import Optional

from prometheus_client import Counter, Histogram

llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["model", "status", "request_type"],
)

llm_tokens_total = Counter(
    "llm_tokens_total",
    "Total tokens processed",
    ["model", "token_type", "request_type"],
)

llm_tokens_per_request = Histogram(
    "llm_tokens_per_request",
    "Token count distribution",
    ["model", "token_type"],
    buckets=[10, 50, 100, 500, 1000, 2000, 4000, 8000],
)

llm_latency_seconds = Histogram(
    "llm_latency_seconds",
    "LLM request latency breakdown",
    ["model", "phase"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60],
)

llm_cost_dollars_total = Counter(
    "llm_cost_dollars_total",
    "Total LLM cost in dollars",
    ["model", "feature"],
)

guardrail_triggers_total = Counter(
    "guardrail_triggers_total",
    "Guardrail trigger count",
    ["guardrail_type", "action"],
)

user_feedback_total = Counter(
    "user_feedback_total",
    "User feedback events",
    ["feedback_type", "sentiment"],
)

llm_evaluation_score = Histogram(
    "llm_evaluation_score",
    "LLM-as-judge evaluation scores (1-5)",
    ["model", "metric_name", "evaluator"],
    buckets=[1, 2, 3, 4, 5],
)

DEFAULT_PRICING = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
}


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    pricing: dict | None = None,
) -> float:
    rates = (pricing or DEFAULT_PRICING).get(model, {"input": 0.01, "output": 0.03})
    return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])


class track_llm_call:
    """Context manager to track LLM calls with latency decomposition."""

    def __init__(self, model: str, request_type: str = "chat", feature: str = "default"):
        self.model = model
        self.request_type = request_type
        self.feature = feature
        self.start_time: float | None = None
        self._ttft_recorded = False

    def __enter__(self) -> track_llm_call:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.start_time is None:
            return
        total_time = time.perf_counter() - self.start_time
        status = "success" if exc_type is None else "error"

        llm_requests_total.labels(
            model=self.model, status=status, request_type=self.request_type
        ).inc()
        llm_latency_seconds.labels(model=self.model, phase="total").observe(total_time)

    def mark_first_token(self) -> None:
        if self.start_time is None or self._ttft_recorded:
            return
        ttft = time.perf_counter() - self.start_time
        record_latency_phase(self.model, "ttft", ttft)
        self._ttft_recorded = True


def record_latency_phase(model: str, phase: str, seconds: float) -> None:
    llm_latency_seconds.labels(model=model, phase=phase).observe(seconds)


def record_ttft(model: str, seconds: float) -> None:
    record_latency_phase(model, "ttft", seconds)


def record_generation_latency(model: str, seconds: float) -> None:
    record_latency_phase(model, "generation", seconds)


def record_tokens(model: str, input_tokens: int, output_tokens: int, request_type: str) -> None:
    llm_tokens_total.labels(model=model, token_type="input", request_type=request_type).inc(
        input_tokens
    )
    llm_tokens_total.labels(model=model, token_type="output", request_type=request_type).inc(
        output_tokens
    )
    llm_tokens_per_request.labels(model=model, token_type="input").observe(input_tokens)
    llm_tokens_per_request.labels(model=model, token_type="output").observe(output_tokens)


def record_cost(model: str, cost: float, feature: str = "default") -> None:
    llm_cost_dollars_total.labels(model=model, feature=feature).inc(cost)


def record_guardrail_trigger(guardrail_type: str, action: str) -> None:
    guardrail_triggers_total.labels(guardrail_type=guardrail_type, action=action).inc()


def record_user_feedback(feedback_type: str, sentiment: str) -> None:
    user_feedback_total.labels(feedback_type=feedback_type, sentiment=sentiment).inc()


def record_evaluation_score(
    model: str,
    metric_name: str,
    score: float,
    evaluator: str = "llm-judge",
) -> None:
    llm_evaluation_score.labels(
        model=model, metric_name=metric_name, evaluator=evaluator
    ).observe(score)