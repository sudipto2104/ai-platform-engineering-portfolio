from platform_assistant.agent.memory import ConversationMemory


def test_conversation_memory_retains_history() -> None:
    memory = ConversationMemory(max_turns=5)
    memory.add("sess-1", "user", "What is a pod?")
    memory.add("sess-1", "assistant", "A pod is the smallest deployable unit.")
    history = memory.format_history("sess-1")
    assert "What is a pod?" in history
    assert "smallest deployable unit" in history


def test_sessions_are_isolated() -> None:
    memory = ConversationMemory()
    memory.add("a", "user", "question a")
    memory.add("b", "user", "question b")
    assert "question a" in memory.format_history("a")
    assert "question a" not in memory.format_history("b")