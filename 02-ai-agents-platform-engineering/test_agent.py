"""Smoke test for the ReAct agent (requires API keys)."""

from __future__ import annotations

import os

import pytest

from platform_agents.react_agent import ask_agent


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
@pytest.mark.skipif(not os.getenv("TAVILY_API_KEY"), reason="TAVILY_API_KEY not set")
def test_react_agent_smoke() -> None:
    answer = ask_agent("What is Kubernetes?")
    assert answer
    assert "ERROR" not in answer


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        print("Skipping live agent test — set OPENAI_API_KEY and TAVILY_API_KEY in .env")
    else:
        print(ask_agent("What is the difference between ArgoCD and Flux?"))
        print("Test completed!")