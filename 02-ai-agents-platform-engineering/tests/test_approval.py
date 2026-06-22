from platform_agents.tools.approval import ApprovalGate


def test_auto_approve_grants_access() -> None:
    gate = ApprovalGate(auto_approve=True)
    decision = gate.request("kubectl apply -f svc.yaml", "apply manifest")
    assert decision.approved
    assert decision.decided_by == "auto"
    assert len(gate.history) == 1