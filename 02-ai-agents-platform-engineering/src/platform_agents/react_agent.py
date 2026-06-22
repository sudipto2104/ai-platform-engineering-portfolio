"""Basic ReAct agent with web search."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()

REACT_SYSTEM_PROMPT = """You are a helpful AI assistant with access to web search.
When asked a question, think step by step.
Use the search tool when you need up-to-date information or facts.
Always provide clear, direct, and well-structured answers."""


def create_react_agent_executor(model: str = "gpt-4o-mini"):
    llm = ChatOpenAI(model=model, temperature=0)
    tools = [TavilySearchResults(max_results=3)]
    system_message = SystemMessage(content=REACT_SYSTEM_PROMPT)
    return create_react_agent(llm, tools, messages_modifier=system_message)


def ask_agent(question: str, model: str = "gpt-4o-mini") -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "ERROR: OPENAI_API_KEY is not configured"
    executor = create_react_agent_executor(model=model)
    response = executor.invoke({"messages": [("user", question)]})
    return response["messages"][-1].content