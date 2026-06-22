from platform_assistant.security.guardrails import (
    assess_kubectl_command,
    filter_output,
    validate_input,
)


def test_blocks_dangerous_kubectl() -> None:
    result = assess_kubectl_command("kubectl delete pod api-1")
    assert not result.allowed


def test_allows_read_only_kubectl() -> None:
    result = assess_kubectl_command("kubectl get pods -n default")
    assert result.allowed


def test_blocks_off_topic_input() -> None:
    result = validate_input("Give me a celebrity gossip recipe")
    assert not result.allowed


def test_filters_sensitive_output() -> None:
    output = filter_output("api_key=sk-secret12345")
    assert "sk-secret12345" not in output
    assert "[REDACTED_SECRET]" in output