import time
from prometheus_client import Counter, Histogram
from typing import Optional

# ====================== METRICS ======================

llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'status', 'request_type']
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total tokens processed',
    ['model', 'token_type', 'request_type']
)

llm_tokens_per_request = Histogram(
    'llm_tokens_per_request',
    'Token count distribution',
    ['model', 'token_type'],
    buckets=[10, 50, 100, 500, 1000, 2000, 4000, 8000]
)

llm_latency_seconds = Histogram(
    'llm_latency_seconds',
    'LLM request latency breakdown',
    ['model', 'phase'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
)

llm_cost_dollars_total = Counter(
    'llm_cost_dollars_total',
    'Total LLM cost in dollars',
    ['model', 'feature']
)

guardrail_triggers_total = Counter(
    'guardrail_triggers_total',
    'Guardrail trigger count',
    ['guardrail_type', 'action']
)

user_feedback_total = Counter(
    'user_feedback_total',
    'User feedback events',
    ['feedback_type', 'sentiment']
)

# ====================== HELPER FUNCTIONS ======================

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = {
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    }
    rates = pricing.get(model, {"input": 0.01, "output": 0.03})
    return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])


class track_llm_call:
    """Context manager to track LLM calls"""
    def __init__(self, model: str, request_type: str = "chat", feature: str = "default"):
        self.model = model
        self.request_type = request_type
        self.feature = feature
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        total_time = time.time() - self.start_time
        status = "success" if exc_type is None else "error"
        
        llm_requests_total.labels(
            model=self.model, status=status, request_type=self.request_type
        ).inc()
        
        llm_latency_seconds.labels(model=self.model, phase="total").observe(total_time)


def record_tokens(model: str, input_tokens: int, output_tokens: int, request_type: str):
    llm_tokens_total.labels(model=model, token_type="input", request_type=request_type).inc(input_tokens)
    llm_tokens_total.labels(model=model, token_type="output", request_type=request_type).inc(output_tokens)
    llm_tokens_per_request.labels(model=model, token_type="input").observe(input_tokens)
    llm_tokens_per_request.labels(model=model, token_type="output").observe(output_tokens)


def record_cost(model: str, cost: float, feature: str = "default"):
    llm_cost_dollars_total.labels(model=model, feature=feature).inc(cost)


def record_guardrail_trigger(guardrail_type: str, action: str):
    guardrail_triggers_total.labels(guardrail_type=guardrail_type, action=action).inc()


def record_user_feedback(feedback_type: str, sentiment: str):
    user_feedback_total.labels(feedback_type=feedback_type, sentiment=sentiment).inc()