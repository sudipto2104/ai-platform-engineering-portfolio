"""Kubernetes tools for the platform assistant agent."""

from __future__ import annotations

import os
import subprocess
from typing import Callable

from langchain_core.tools import tool

from platform_agents.tools.approval import ApprovalGate
from platform_agents.tools.guardrails import assess_command, assess_tool_call

MOCK_PODS = {
    "default": "NAME           READY   STATUS    RESTARTS   AGE\napi-7d8f9c   1/1     Running   0          2d\nworker-abc   0/1     CrashLoopBackOff   5   1h",
    "kube-system": "NAME                 READY   STATUS    RESTARTS   AGE\ncoredns-55c          1/1     Running   0          9d\nkube-proxy-xyz       1/1     Running   0          9d",
}


def _dry_run_enabled() -> bool:
    return os.getenv("K8S_DRY_RUN", "false").lower() == "true"


def _run_kubectl(args: list[str], approval_gate: ApprovalGate | None = None) -> str:
    command = "kubectl " + " ".join(args)
    guardrail = assess_command(command)
    if not guardrail.allowed:
        return f"BLOCKED: {guardrail.reason}"

    if guardrail.requires_approval:
        gate = approval_gate or ApprovalGate()
        decision = gate.request(action=command, details=guardrail.reason)
        if not decision.approved:
            return f"DENIED: {decision.reason}"

    if _dry_run_enabled():
        return f"[dry-run] {command}"

    try:
        result = subprocess.run(
            ["kubectl", *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except FileNotFoundError:
        return "ERROR: kubectl not found in PATH"
    except subprocess.TimeoutExpired:
        return "ERROR: kubectl command timed out"

    if result.returncode != 0:
        return result.stderr.strip() or result.stdout.strip() or "kubectl command failed"
    return result.stdout.strip()


def build_k8s_tools(approval_gate: ApprovalGate | None = None) -> list[Callable]:
    gate = approval_gate or ApprovalGate()

    @tool
    def get_pods(namespace: str = "default") -> str:
        """List all pods in a Kubernetes namespace."""
        check = assess_tool_call("get_pods", {"namespace": namespace})
        if not check.allowed:
            return f"BLOCKED: {check.reason}"
        if _dry_run_enabled():
            return MOCK_PODS.get(namespace, MOCK_PODS["default"])
        return _run_kubectl(["get", "pods", "-n", namespace], approval_gate=gate)

    @tool
    def get_pod_logs(pod_name: str, namespace: str = "default", tail: int = 50) -> str:
        """Fetch recent logs for a Kubernetes pod."""
        check = assess_tool_call("get_pod_logs", {"pod_name": pod_name, "namespace": namespace})
        if not check.allowed:
            return f"BLOCKED: {check.reason}"
        if _dry_run_enabled():
            return (
                f"[dry-run] logs for {pod_name} in {namespace}\n"
                "INFO: server started\nERROR: connection refused on :8080"
            )
        return _run_kubectl(
            ["logs", pod_name, "-n", namespace, f"--tail={tail}"],
            approval_gate=gate,
        )

    @tool
    def describe_pod(pod_name: str, namespace: str = "default") -> str:
        """Describe a Kubernetes pod including events and probe status."""
        check = assess_tool_call("describe_pod", {"pod_name": pod_name, "namespace": namespace})
        if not check.allowed:
            return f"BLOCKED: {check.reason}"
        if _dry_run_enabled():
            return (
                f"Name: {pod_name}\nNamespace: {namespace}\nStatus: Running\n"
                "Events:\n  Warning  Unhealthy  Readiness probe failed"
            )
        return _run_kubectl(["describe", "pod", pod_name, "-n", namespace], approval_gate=gate)

    return [get_pods, get_pod_logs, describe_pod]