from platform_agents.tools.guardrails import assess_command, assess_tool_call


def test_blocks_delete_commands() -> None:
    result = assess_command("kubectl delete pod api-123 -n prod")
    assert not result.allowed
    assert result.risk_level.value == "high"


def test_requires_approval_for_apply() -> None:
    result = assess_command("kubectl apply -f deployment.yaml")
    assert result.allowed
    assert result.requires_approval


def test_allows_read_only_tool_calls() -> None:
    result = assess_tool_call("get_pods", {"namespace": "default"})
    assert result.allowed
    assert not result.requires_approval