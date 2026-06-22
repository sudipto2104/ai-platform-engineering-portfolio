#!/usr/bin/env python3
"""Example: log a prompt evaluation run to MLflow."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "mlflow-integration"))

from mlflow_tracker import LLMRunMetrics, MLflowLLMTracker, PromptVersion


def main() -> None:
    tracker = MLflowLLMTracker()

    prompt = PromptVersion(
        name="platform-assistant-v1.3",
        template=(
            "You are a Platform Engineering assistant.\n"
            "Use the provided context to answer: {question}\n"
            "Always cite sources."
        ),
        model="gpt-4o-mini",
        temperature=0.1,
        metadata={"feature": "rag-qa", "chunk_size": 600},
    )

    metrics = LLMRunMetrics(
        relevance_score=4.6,
        faithfulness_score=4.8,
        latency_ms=842.0,
        input_tokens=1240,
        output_tokens=186,
        total_tokens=1426,
        cost_usd=0.00034,
    )

    run_id = tracker.log_evaluation(
        prompt=prompt,
        metrics=metrics,
        run_name="prompt-v1.3",
        tags={"environment": "dev", "evaluator": "llm-judge"},
    )
    print(f"Logged run: {run_id}")
    print(f"View at: {tracker.tracking_uri}")


if __name__ == "__main__":
    main()