from __future__ import annotations

import os
import subprocess
from typing import Callable

from langchain_core.tools import tool

from platform_assistant.config import Settings
from platform_assistant.observability.metrics import rag_retrievals_total
from platform_assistant.rag.store import RAGStore
from platform_assistant.security.guardrails import assess_kubectl_command

MOCK_PODS = (
    "NAME           READY   STATUS    RESTARTS   AGE\n"
    "api-7d8f9c     1/1     Running   0          2d\n"
    "worker-failed  0/1     CrashLoopBackOff   5   1h"
)


def build_tools(settings: Settings, rag_store: RAGStore) -> list[Callable]:
    @tool
    def search_documentation(query: str) -> str:
        """Search Kubernetes and platform engineering documentation."""
        docs = rag_store.search(query, top_k=settings.retrieval_top_k)
        if not docs:
            rag_retrievals_total.labels(status="empty").inc()
            return "No relevant documentation found."
        rag_retrievals_total.labels(status="success").inc()
        blocks = []
        for i, doc in enumerate(docs, start=1):
            blocks.append(f"[{i}] {doc.text}\nSource: {doc.citation}")
        return "\n\n".join(blocks)

    @tool
    def kubectl_read_only(command: str) -> str:
        """Execute read-only kubectl commands (get, describe, logs only)."""
        check = assess_kubectl_command(command)
        if not check.allowed:
            return f"BLOCKED: {check.reason}"

        if settings.k8s_dry_run or os.getenv("K8S_DRY_RUN", "true").lower() == "true":
            if "get pods" in command:
                return MOCK_PODS
            return f"[dry-run] {command}"

        args = command.split()[1:] if command.startswith("kubectl ") else command.split()
        try:
            result = subprocess.run(
                ["kubectl", *args],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except FileNotFoundError:
            return "ERROR: kubectl not found"
        except subprocess.TimeoutExpired:
            return "ERROR: kubectl timed out"

        if result.returncode != 0:
            return result.stderr.strip() or "kubectl failed"
        return result.stdout.strip()

    @tool
    def generate_kubectl_command(intent: str) -> str:
        """Generate a safe read-only kubectl command for the user's intent."""
        lowered = intent.lower()
        if "log" in lowered:
            return "kubectl logs <pod-name> -n <namespace> --tail=50"
        if "describe" in lowered:
            return "kubectl describe pod <pod-name> -n <namespace>"
        if "namespace" in lowered:
            return "kubectl get pods -n <namespace>"
        return "kubectl get pods -A"

    return [search_documentation, kubectl_read_only, generate_kubectl_command]