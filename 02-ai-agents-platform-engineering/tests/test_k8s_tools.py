import os

from platform_agents.tools.k8s_tools import build_k8s_tools


def test_get_pods_dry_run(monkeypatch) -> None:
    monkeypatch.setenv("K8S_DRY_RUN", "true")
    tools = {tool.name: tool for tool in build_k8s_tools()}
    output = tools["get_pods"].invoke({"namespace": "default"})
    assert "api-7d8f9c" in output


def test_get_pod_logs_dry_run(monkeypatch) -> None:
    monkeypatch.setenv("K8S_DRY_RUN", "true")
    tools = {tool.name: tool for tool in build_k8s_tools()}
    output = tools["get_pod_logs"].invoke({"pod_name": "api-7d8f9c", "namespace": "default"})
    assert "connection refused" in output