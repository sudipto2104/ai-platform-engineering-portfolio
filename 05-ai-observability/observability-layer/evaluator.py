"""LLM-as-judge evaluation framework with Prometheus integration."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ai_observability import record_evaluation_score


@dataclass
class EvaluationInput:
    question: str
    answer: str
    context: str = ""
    model: str = "gpt-4o-mini"


@dataclass
class EvaluationResult:
    relevance: float
    faithfulness: float
    conciseness: float
    evaluator: str = "llm-judge"
    notes: dict[str, str] = field(default_factory=dict)

    def average_score(self) -> float:
        return round((self.relevance + self.faithfulness + self.conciseness) / 3, 2)

    def to_dict(self) -> dict[str, float]:
        return {
            "relevance": self.relevance,
            "faithfulness": self.faithfulness,
            "conciseness": self.conciseness,
            "average": self.average_score(),
        }


class LLMJudgeEvaluator:
    """Heuristic evaluator for offline demos; swap with real LLM judge in production."""

    def evaluate(self, sample: EvaluationInput) -> EvaluationResult:
        answer = sample.answer.strip()
        context = sample.context.strip()

        relevance = self._score_relevance(sample.question, answer)
        faithfulness = self._score_faithfulness(answer, context)
        conciseness = self._score_conciseness(answer)

        return EvaluationResult(
            relevance=relevance,
            faithfulness=faithfulness,
            conciseness=conciseness,
            notes={"mode": "heuristic", "question_length": str(len(sample.question))},
        )

    def evaluate_and_record(self, sample: EvaluationInput) -> EvaluationResult:
        result = self.evaluate(sample)
        for metric_name, score in result.to_dict().items():
            if metric_name == "average":
                continue
            record_evaluation_score(sample.model, metric_name, score, result.evaluator)
        record_evaluation_score(sample.model, "average", result.average_score(), result.evaluator)
        return result

    def _score_relevance(self, question: str, answer: str) -> float:
        if not answer:
            return 1.0
        question_terms = set(re.findall(r"[a-zA-Z]{4,}", question.lower()))
        answer_terms = set(re.findall(r"[a-zA-Z]{4,}", answer.lower()))
        if not question_terms:
            return 3.0
        overlap = len(question_terms & answer_terms) / len(question_terms)
        return min(5.0, max(1.0, 2.0 + overlap * 3))

    def _score_faithfulness(self, answer: str, context: str) -> float:
        if not context:
            return 3.5
        context_terms = set(re.findall(r"[a-zA-Z]{4,}", context.lower()))
        answer_terms = set(re.findall(r"[a-zA-Z]{4,}", answer.lower()))
        if not answer_terms:
            return 1.0
        grounded = len(answer_terms & context_terms) / len(answer_terms)
        return min(5.0, max(1.0, 1.5 + grounded * 3.5))

    def _score_conciseness(self, answer: str) -> float:
        words = len(answer.split())
        if words <= 80:
            return 5.0
        if words <= 160:
            return 4.0
        if words <= 300:
            return 3.0
        return 2.0