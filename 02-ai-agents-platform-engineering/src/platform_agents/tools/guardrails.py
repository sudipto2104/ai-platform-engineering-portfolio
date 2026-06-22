"""Guardrails for safe tool execution."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


BLOCKED_PATTERNS = [
    r"\bkubectl\s+delete\b",
    r"\bkubectl\s+drain\b",
    r"\bkubectl\s+cordon\b",
    r"\brm\s+-rf\b",
    r"\bdd\s+if=",
    r"\bmkfs\b",
]

APPROVAL_PATTERNS = [
    r"\bkubectl\s+apply\b",
    r"\bkubectl\s+patch\b",
    r"\bkubectl\s+scale\b",
    r"\bkubectl\s+rollout\b",
    r"\bkubectl\s+exec\b",
]


@dataclass
class GuardrailResult:
    allowed: bool
    risk_level: RiskLevel
    reason: str
    requires_approval: bool = False


def assess_command(command: str) -> GuardrailResult:
    normalized = command.strip().lower()

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, normalized):
            return GuardrailResult(
                allowed=False,
                risk_level=RiskLevel.HIGH,
                reason=f"Blocked dangerous command pattern: {pattern}",
            )

    for pattern in APPROVAL_PATTERNS:
        if re.search(pattern, normalized):
            return GuardrailResult(
                allowed=True,
                risk_level=RiskLevel.MEDIUM,
                reason="Write or exec operation requires human approval",
                requires_approval=True,
            )

    return GuardrailResult(
        allowed=True,
        risk_level=RiskLevel.LOW,
        reason="Read-only or safe operation",
    )


def assess_tool_call(tool_name: str, arguments: dict | None = None) -> GuardrailResult:
    arguments = arguments or {}
    if tool_name in {"delete_pod", "scale_deployment", "apply_manifest"}:
        return GuardrailResult(
            allowed=False,
            risk_level=RiskLevel.HIGH,
            reason=f"Tool '{tool_name}' is disabled by policy",
        )

    if tool_name in {"get_pod_logs", "describe_pod"}:
        return GuardrailResult(
            allowed=True,
            risk_level=RiskLevel.LOW,
            reason="Read-only Kubernetes inspection",
        )

    serialized = f"{tool_name} {arguments}"
    return assess_command(serialized)