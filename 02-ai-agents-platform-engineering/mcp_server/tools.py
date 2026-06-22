"""MCP tool registry for Kubernetes platform operations."""

from __future__ import annotations

import os
from typing import Any, Callable

from platform_agents.tools.approval import ApprovalGate
from platform_agents.tools.k8s_tools import _dry_run_enabled, _run_kubectl

MOCK_PODS = {
    "default": "NAME           READY   STATUS    RESTARTS   AGE\napi-7d8f9c   1/1     Running   0          2d",
}


def _get_pods(namespace: str = "default") -> str:
    if _dry_run_enabled():
        return MOCK_PODS.get(namespace, MOCK_PODS["default"])
    return _run_kubectl(["get", "pods", "-n", namespace], approval_gate=ApprovalGate(auto_approve=True))


def _get_pod_logs(pod_name: str, namespace: str = "default", tail: int = 50) -> str:
    if _dry_run_enabled():
        return f"[dry-run] logs for {pod_name} in {namespace}"
    return _run_kubectl(
        ["logs", pod_name, "-n", namespace, f"--tail={tail}"],
        approval_gate=ApprovalGate(auto_approve=True),
    )


def _describe_pod(pod_name: str, namespace: str = "default") -> str:
    if _dry_run_enabled():
        return f"Name: {pod_name}\nNamespace: {namespace}\nStatus: Running"
    return _run_kubectl(
        ["describe", "pod", pod_name, "-n", namespace],
        approval_gate=ApprovalGate(auto_approve=True),
    )


TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    "get_pods": {
        "description": "List all pods in a Kubernetes namespace",
        "inputSchema": {
            "type": "object",
            "properties": {"namespace": {"type": "string", "default": "default"}},
        },
        "handler": _get_pods,
    },
    "get_pod_logs": {
        "description": "Fetch recent logs for a Kubernetes pod",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string"},
                "namespace": {"type": "string", "default": "default"},
                "tail": {"type": "integer", "default": 50},
            },
            "required": ["pod_name"],
        },
        "handler": _get_pod_logs,
    },
    "describe_pod": {
        "description": "Describe a Kubernetes pod including events",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string"},
                "namespace": {"type": "string", "default": "default"},
            },
            "required": ["pod_name"],
        },
        "handler": _describe_pod,
    },
}


def list_tools() -> list[dict[str, Any]]:
    return [
        {"name": name, "description": meta["description"], "inputSchema": meta["inputSchema"]}
        for name, meta in TOOL_REGISTRY.items()
    ]


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> str:
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")
    handler: Callable = TOOL_REGISTRY[name]["handler"]
    return handler(**(arguments or {}))