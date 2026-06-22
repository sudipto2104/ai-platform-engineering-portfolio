import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "mlflow-integration"))

from mlflow_tracker import LLMRunMetrics, MLflowLLMTracker, PromptVersion


@pytest.fixture
def tracker() -> MLflowLLMTracker:
    with patch("mlflow_tracker.mlflow"), patch("mlflow_tracker.MlflowClient"):
        return MLflowLLMTracker(tracking_uri="http://localhost:5000")


def test_llm_run_metrics_flattens_extra() -> None:
    metrics = LLMRunMetrics(
        relevance_score=4.5,
        faithfulness_score=4.7,
        extra={"hallucination_rate": 0.02},
    )
    result = metrics.to_mlflow_dict()
    assert result["relevance_score"] == 4.5
    assert result["faithfulness_score"] == 4.7
    assert result["hallucination_rate"] == 0.02
    assert "extra" not in result


@patch("mlflow_tracker.mlflow")
def test_log_prompt_writes_params_and_artifacts(mock_mlflow: MagicMock, tracker: MLflowLLMTracker) -> None:
    prompt = PromptVersion(
        name="test-prompt",
        template="Answer: {question}",
        model="gpt-4o-mini",
        temperature=0.2,
        metadata={"version": "1"},
    )

    tracker.log_prompt(prompt)

    mock_mlflow.log_param.assert_any_call("prompt_name", "test-prompt")
    mock_mlflow.log_param.assert_any_call("model", "gpt-4o-mini")
    mock_mlflow.log_param.assert_any_call("temperature", 0.2)
    mock_mlflow.log_param.assert_any_call("meta_version", "1")
    assert mock_mlflow.log_artifact.call_count == 2


@patch("mlflow_tracker.mlflow")
def test_log_metrics(mock_mlflow: MagicMock, tracker: MLflowLLMTracker) -> None:
    metrics = LLMRunMetrics(latency_ms=500.0, input_tokens=100, output_tokens=50)
    tracker.log_metrics(metrics)

    mock_mlflow.log_metric.assert_any_call("latency_ms", 500.0)
    mock_mlflow.log_metric.assert_any_call("input_tokens", 100.0)
    mock_mlflow.log_metric.assert_any_call("output_tokens", 50.0)