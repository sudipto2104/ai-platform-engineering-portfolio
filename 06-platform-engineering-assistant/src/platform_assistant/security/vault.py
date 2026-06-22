"""HashiCorp Vault integration for secrets management."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


@dataclass
class VaultSecrets:
    openai_api_key: str = ""
    tavily_api_key: str = ""
    ollama_api_key: str = ""


class VaultClient:
    def __init__(
        self,
        addr: str | None = None,
        token: str | None = None,
        secret_path: str = "secret/data/platform-assistant",
    ):
        self.addr = (addr or os.getenv("VAULT_ADDR", "http://localhost:8200")).rstrip("/")
        self.token = token or os.getenv("VAULT_TOKEN", "")
        self.secret_path = secret_path or os.getenv("VAULT_SECRET_PATH", "secret/data/platform-assistant")
        self._local_fallback = Path(os.getenv("VAULT_LOCAL_SECRETS", "./config/local-secrets.json"))

    def _use_local_fallback(self) -> bool:
        return os.getenv("VAULT_USE_LOCAL", "true").lower() == "true" or not self.token

    def read_secrets(self) -> VaultSecrets:
        if self._use_local_fallback() and self._local_fallback.exists():
            data = json.loads(self._local_fallback.read_text(encoding="utf-8"))
            return VaultSecrets(**{k: data.get(k, "") for k in VaultSecrets.__annotations__})

        try:
            response = httpx.get(
                f"{self.addr}/v1/{self.secret_path}",
                headers={"X-Vault-Token": self.token},
                timeout=5.0,
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json().get("data", {}).get("data", {})
            return VaultSecrets(
                openai_api_key=payload.get("openai_api_key", ""),
                tavily_api_key=payload.get("tavily_api_key", ""),
                ollama_api_key=payload.get("ollama_api_key", ""),
            )
        except Exception:
            return VaultSecrets()