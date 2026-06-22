import sys
from pathlib import Path

import pytest

OBS_DIR = Path(__file__).resolve().parents[1] / "observability-layer"
sys.path.insert(0, str(OBS_DIR))

from ai_observability import calculate_cost, track_llm_call  # noqa: E402


def test_calculate_cost_gpt4o_mini() -> None:
    cost = calculate_cost("gpt-4o-mini", input_tokens=1000, output_tokens=500)
    assert cost == pytest.approx(0.00015 + 0.0003, rel=1e-6)


def test_calculate_cost_unknown_model_uses_default_rates() -> None:
    cost = calculate_cost("unknown-model", input_tokens=1000, output_tokens=1000)
    assert cost == pytest.approx(0.04, rel=1e-6)


def test_track_llm_call_context_manager_does_not_raise() -> None:
    with track_llm_call(model="gpt-4o-mini", request_type="rag", feature="test"):
        pass