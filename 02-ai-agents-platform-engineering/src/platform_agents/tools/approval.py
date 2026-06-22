"""Human-in-the-loop approval workflow."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ApprovalRequest:
    action: str
    details: str
    requested_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class ApprovalDecision:
    approved: bool
    action: str
    decided_by: str
    reason: str = ""


class ApprovalGate:
    """Gate dangerous operations behind explicit human approval."""

    def __init__(self, auto_approve: bool | None = None):
        if auto_approve is None:
            auto_approve = os.getenv("AUTO_APPROVE", "false").lower() == "true"
        self.auto_approve = auto_approve
        self._history: list[ApprovalDecision] = []

    def request(self, action: str, details: str) -> ApprovalDecision:
        if self.auto_approve:
            decision = ApprovalDecision(
                approved=True,
                action=action,
                decided_by="auto",
                reason="AUTO_APPROVE enabled",
            )
            self._history.append(decision)
            return decision

        print("\n=== Human Approval Required ===")
        print(f"Action:  {action}")
        print(f"Details: {details}")
        response = input("Approve this action? [y/N]: ").strip().lower()
        approved = response in {"y", "yes"}
        decision = ApprovalDecision(
            approved=approved,
            action=action,
            decided_by="human",
            reason="approved by operator" if approved else "denied by operator",
        )
        self._history.append(decision)
        return decision

    @property
    def history(self) -> list[ApprovalDecision]:
        return list(self._history)