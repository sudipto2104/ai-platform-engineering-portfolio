from __future__ import annotations

import re
from dataclasses import dataclass

BLOCKED_INPUT_PATTERNS = [
    r"\bpassword\s*[:=]",
    r"\bapi[_-]?key\s*[:=]",
    r"\bsecret\s*[:=]",
    r"\bkubectl\s+delete\b",
    r"\bkubectl\s+drain\b",
    r"\bkubectl\s+cordon\b",
    r"\brm\s+-rf\s+/",
]

OFF_TOPIC_PATTERNS = [
    r"\brecipe\b",
    r"\bstock\s+price\b",
    r"\bcelebrity\b",
    r"\bgossip\b",
]

SENSITIVE_OUTPUT_PATTERNS = [
    (r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S+", "[REDACTED_SECRET]"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
]


@dataclass
class ValidationResult:
    allowed: bool
    reason: str = ""


def validate_input(text: str) -> ValidationResult:
    normalized = text.strip()
    if not normalized:
        return ValidationResult(allowed=False, reason="Empty input")
    if len(normalized) > 4000:
        return ValidationResult(allowed=False, reason="Input exceeds maximum length")

    for pattern in BLOCKED_INPUT_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return ValidationResult(allowed=False, reason=f"Blocked pattern detected: {pattern}")

    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return ValidationResult(
                allowed=False,
                reason="Request appears off-topic for platform engineering",
            )

    return ValidationResult(allowed=True)


def filter_output(text: str) -> str:
    filtered = text
    for pattern, replacement in SENSITIVE_OUTPUT_PATTERNS:
        filtered = re.sub(pattern, replacement, filtered)
    return filtered


def assess_kubectl_command(command: str) -> ValidationResult:
    normalized = command.strip().lower()
    write_ops = ["apply", "delete", "patch", "scale", "exec", "drain", "cordon"]
    if not normalized.startswith("kubectl "):
        return ValidationResult(allowed=False, reason="Only kubectl commands are supported")
    for op in write_ops:
        if f"kubectl {op}" in normalized or f"kubectl  {op}" in normalized:
            return ValidationResult(allowed=False, reason=f"Write operation '{op}' is not permitted")
    return ValidationResult(allowed=True)