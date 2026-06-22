"""Backward-compatible entrypoint for the basic ReAct agent."""

from platform_agents.react_agent import ask_agent, create_react_agent_executor

__all__ = ["ask_agent", "create_react_agent_executor"]


if __name__ == "__main__":
    print("AI Agent is ready! (Powered by LangGraph + Tavily)\n")
    ask_agent("What are the latest developments in Kubernetes in 2026?")