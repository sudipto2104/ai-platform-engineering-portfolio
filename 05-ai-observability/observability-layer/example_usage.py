"""Integration example for AI observability."""

from __future__ import annotations

import time

from ai_observability import (
    calculate_cost,
    record_cost,
    record_generation_latency,
    record_guardrail_trigger,
    record_tokens,
    record_user_feedback,
    track_llm_call,
)
from evaluator import EvaluationInput, LLMJudgeEvaluator


def generate_response(question: str, model: str = "gpt-4o-mini") -> str:
    with track_llm_call(model=model, request_type="rag", feature="platform_assistant") as tracker:
        time.sleep(0.08)
        tracker.mark_first_token()

        time.sleep(0.12)
        record_generation_latency(model, 0.12)

        input_tokens = 850
        output_tokens = 320
        record_tokens(model, input_tokens, output_tokens, request_type="rag")

        cost = calculate_cost(model, input_tokens, output_tokens)
        record_cost(model, cost, feature="platform_assistant")

        answer = (
            "Check pod status with `kubectl get pods -n <namespace>` and "
            "`kubectl describe pod <name>` for events and probe failures."
        )

        if "password" in question.lower():
            record_guardrail_trigger("pii_filter", "blocked")

        evaluator = LLMJudgeEvaluator()
        evaluator.evaluate_and_record(
            EvaluationInput(
                question=question,
                answer=answer,
                context="kubectl get pods shows pod phase and readiness.",
                model=model,
            )
        )
        return answer


if __name__ == "__main__":
    response = generate_response("How do I check pod status in Kubernetes?")
    print(response)
    record_user_feedback("thumbs", "positive")