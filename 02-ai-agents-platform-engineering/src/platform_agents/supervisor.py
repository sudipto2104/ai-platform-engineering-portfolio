"""Multi-agent supervisor routing to specialist agents."""

from __future__ import annotations

import os
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from platform_agents.platform_assistant import create_platform_assistant
from platform_agents.react_agent import create_react_agent_executor
from platform_agents.tools.approval import ApprovalGate

load_dotenv()

K8S_KEYWORDS = {
    "pod",
    "pods",
    "kubernetes",
    "k8s",
    "namespace",
    "deployment",
    "logs",
    "crashloop",
    "node",
    "cluster",
}


class SupervisorState(TypedDict):
    question: str
    route: str
    answer: str


def route_question(question: str) -> Literal["kubernetes", "search"]:
    lowered = question.lower()
    if any(keyword in lowered for keyword in K8S_KEYWORDS):
        return "kubernetes"
    return "search"


def _supervisor_node(state: SupervisorState) -> SupervisorState:
    route = route_question(state["question"])
    return {**state, "route": route}


def _kubernetes_node(state: SupervisorState) -> SupervisorState:
    gate = ApprovalGate()
    agent = create_platform_assistant(approval_gate=gate)
    response = agent.invoke({"messages": [HumanMessage(content=state["question"])]})
    return {**state, "answer": response["messages"][-1].content}


def _search_node(state: SupervisorState) -> SupervisorState:
    agent = create_react_agent_executor()
    response = agent.invoke({"messages": [HumanMessage(content=state["question"])]})
    return {**state, "answer": response["messages"][-1].content}


def _route_decision(state: SupervisorState) -> str:
    return state["route"]


def build_supervisor_graph():
    graph = StateGraph(SupervisorState)
    graph.add_node("supervisor", _supervisor_node)
    graph.add_node("kubernetes", _kubernetes_node)
    graph.add_node("search", _search_node)
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        _route_decision,
        {"kubernetes": "kubernetes", "search": "search"},
    )
    graph.add_edge("kubernetes", END)
    graph.add_edge("search", END)
    return graph.compile()


def ask_supervisor(question: str) -> dict[str, str]:
    if not os.getenv("OPENAI_API_KEY"):
        return {"route": "none", "answer": "ERROR: OPENAI_API_KEY is not configured"}

    workflow = build_supervisor_graph()
    result = workflow.invoke({"question": question, "route": "", "answer": ""})
    return {"route": result["route"], "answer": result["answer"]}