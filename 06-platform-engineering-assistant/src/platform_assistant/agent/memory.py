from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class ChatTurn:
    role: str
    content: str


class ConversationMemory:
    """In-memory conversation store with per-session history."""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._sessions: dict[str, deque[ChatTurn]] = defaultdict(lambda: deque(maxlen=max_turns * 2))

    def add(self, session_id: str, role: str, content: str) -> None:
        self._sessions[session_id].append(ChatTurn(role=role, content=content))

    def get_history(self, session_id: str) -> list[ChatTurn]:
        return list(self._sessions.get(session_id, []))

    def format_history(self, session_id: str) -> str:
        turns = self.get_history(session_id)
        if not turns:
            return ""
        lines = [f"{turn.role}: {turn.content}" for turn in turns[-self.max_turns :]]
        return "\n".join(lines)

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)