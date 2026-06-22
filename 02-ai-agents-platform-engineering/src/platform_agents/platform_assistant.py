"""Platform assistant agent with Kubernetes tools and guardrails."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from platform_agents.tools.approval import ApprovalGate
from platform_agents.tools.k8s_tools import build_k8s_tools

load_dotenv()

PLATFORM_SYSTEM_PROMPT = """You are a Platform Engineering assistant with Kubernetes tools.
Use get_pods, get_pod_logs, and describe_pod to investigate cluster issues.
Never attempt destructive operations. Explain findings clearly for operators.
If a tool response says BLOCKED or DENIED, explain the safety policy to the user."""


def create_platform_assistant(approval_gate: ApprovalGate | None = None, model: str = "gpt-4o-mini"):
    llm = ChatOpenAI(model=model, temperature=0)
    tools = build_k8s_tools(approval_gate=approval_gate)
    system_message = SystemMessage(content=PLATFORM_SYSTEM_PROMPT)
    return create_react_agent(llm, tools, messages_modifier=system_message)


def ask_platform_assistant(
    question: str,
    approval_gate: ApprovalGate | None = None,
    model: str = "gpt-4o-mini",
) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "ERROR: OPENAI_API_KEY is not configured"
    executor = create_platform_assistant(approval_gate=approval_gate, model=model)
    response = executor.invoke({"messages": [("user", question)]})
    return response["messages"][-1].content