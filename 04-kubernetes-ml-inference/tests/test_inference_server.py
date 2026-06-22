import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "inference-server" / "app.py"


@pytest.fixture
def client() -> TestClient:
    spec = importlib.util.spec_from_file_location("inference_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["inference_app"] = module
    spec.loader.exec_module(module)
    return TestClient(module.app)


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predict_endpoint(client: TestClient) -> None:
    response = client.post(
        "/predict",
        json={"input_text": "schedule inference pod", "max_tokens": 32},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"].startswith("label-")
    assert body["latency_ms"] > 0