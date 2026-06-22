from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


def setup_logging(level: str = "INFO") -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )
    return logging.getLogger("platform_assistant")


def log_request_response(
    logger: logging.Logger,
    *,
    session_id: str,
    question: str,
    answer: str,
    model: str,
    citations: list[str] | None = None,
    tools_used: list[str] | None = None,
    latency_ms: float = 0.0,
) -> None:
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "model": model,
        "question": question,
        "answer": answer,
        "citations": citations or [],
        "tools_used": tools_used or [],
        "latency_ms": round(latency_ms, 2),
    }
    logger.info("request_response %s", json.dumps(payload))