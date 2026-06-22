import os

from fastapi.testclient import TestClient

from mcp_server.server import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_tools_list_and_call(monkeypatch) -> None:
    monkeypatch.setenv("K8S_DRY_RUN", "true")
    client = TestClient(app)

    tools_response = client.get("/tools")
    assert tools_response.status_code == 200
    tools = tools_response.json()["tools"]
    assert any(tool["name"] == "get_pods" for tool in tools)

    call_response = client.post(
        "/tools/call",
        json={"name": "get_pods", "arguments": {"namespace": "default"}},
    )
    assert call_response.status_code == 200
    assert "api-7d8f9c" in call_response.json()["content"]


def test_mcp_jsonrpc_tools_list() -> None:
    client = TestClient(app)
    response = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["result"]["tools"]