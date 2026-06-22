#!/usr/bin/env python3
"""Generate sample observability metrics for local demos."""

from __future__ import annotations

import sys
import time
from pathlib import Path

OBS_DIR = Path(__file__).resolve().parents[1] / "observability-layer"
sys.path.insert(0, str(OBS_DIR))

from example_usage import generate_response  # noqa: E402
from ai_observability import record_user_feedback  # noqa: E402


def main() -> None:
    questions = [
        "How do I check pod status in Kubernetes?",
        "What is a ResourceQuota?",
        "How do I debug OOMKilled inference pods?",
    ]
    for question in questions:
        print(f"Q: {question}")
        answer = generate_response(question)
        print(f"A: {answer}\n")
        time.sleep(0.2)

    record_user_feedback("thumbs", "positive")
    print("Demo complete. Scrape http://localhost:8000/metrics")


if __name__ == "__main__":
    main()