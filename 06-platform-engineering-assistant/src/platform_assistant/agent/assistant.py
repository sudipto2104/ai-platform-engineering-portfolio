from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from platform_assistant.agent.memory import ConversationMemory
from platform_assistant.agent.tools import build_tools
from platform_assistant.config import Settings
from platform_assistant.observability.metrics import estimate_ollama_cost, record_tokens, track_request
from platform_assistant.rag.store import RAGStore
from platform_assistant.security.guardrails import filter_output, validate_input

SYSTEM_PROMPT = """You are a Platform Engineering Assistant for Kubernetes and infrastructure operations.
Use search_documentation for conceptual questions.
Use kubectl_read_only for cluster inspection (read-only only).
Use generate_kubectl_command to suggest safe commands.
Refuse dangerous, off-topic, or destructive requests.
Always cite documentation sources when using retrieved context."""


@dataclass
class AssistantResponse:
    answer: str
    citations: list[str] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    session_id: str = ""
    latency_ms: float = 0.0


class PlatformAssistant:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings.load()
        self.rag_store = RAGStore(self.settings)
        self.memory = ConversationMemory()
        self._llm = ChatOllama(
            base_url=self.settings.ollama_base_url,
            model=self.settings.ollama_model,
            temperature=0,
        )
        tools = build_tools(self.settings, self.rag_store)
        self._agent = create_react_agent(
            self._llm,
            tools,
            prompt=SYSTEM_PROMPT,
        )

    def chat(self, question: str, session_id: str = "default") -> AssistantResponse:
        validation = validate_input(question)
        if not validation.allowed:
            return AssistantResponse(
                answer=f"I cannot process this request: {validation.reason}",
                session_id=session_id,
            )

        history = self.memory.format_history(session_id)
        prompt = question if not history else f"Conversation history:\n{history}\n\nNew question: {question}"

        start = time.perf_counter()
        with track_request(model=self.settings.ollama_model, request_type="platform_assistant"):
            try:
                result = self._agent.invoke({"messages": [HumanMessage(content=prompt)]})
                raw_answer = result["messages"][-1].content
            except Exception as exc:
                raw_answer = (
                    f"I encountered an error connecting to the LLM ({self.settings.ollama_model}). "
                    f"Ensure Ollama is running. Details: {exc}"
                )

        answer = filter_output(raw_answer)
        latency_ms = (time.perf_counter() - start) * 1000

        citations = re.findall(r"\[[^\]]+#chunk-\d+\]", answer)
        input_tokens = len(prompt.split())
        output_tokens = len(answer.split())
        record_tokens(self.settings.ollama_model, input_tokens, output_tokens)
        estimate_ollama_cost(self.settings.ollama_model, input_tokens + output_tokens)

        self.memory.add(session_id, "user", question)
        self.memory.add(session_id, "assistant", answer)

        return AssistantResponse(
            answer=answer,
            citations=citations,
            session_id=session_id,
            latency_ms=latency_ms,
        )