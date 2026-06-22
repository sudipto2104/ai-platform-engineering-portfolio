import sys
from pathlib import Path

OBS_DIR = Path(__file__).resolve().parents[1] / "observability-layer"
sys.path.insert(0, str(OBS_DIR))

from evaluator import EvaluationInput, LLMJudgeEvaluator


def test_evaluator_returns_scores_in_range() -> None:
    evaluator = LLMJudgeEvaluator()
    result = evaluator.evaluate(
        EvaluationInput(
            question="How do I check Kubernetes pod status?",
            answer="Use kubectl get pods to check pod status in your namespace.",
            context="kubectl get pods lists pod phase and readiness.",
            model="gpt-4o-mini",
        )
    )

    assert 1.0 <= result.relevance <= 5.0
    assert 1.0 <= result.faithfulness <= 5.0
    assert 1.0 <= result.conciseness <= 5.0
    assert 1.0 <= result.average_score() <= 5.0


def test_conciseness_penalizes_long_answers() -> None:
    evaluator = LLMJudgeEvaluator()
    short = evaluator._score_conciseness("short answer")
    long = evaluator._score_conciseness("word " * 400)
    assert short > long