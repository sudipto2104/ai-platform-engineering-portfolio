import json
from pathlib import Path

from platform_assistant.security.vault import VaultClient


def test_local_vault_fallback(tmp_path, monkeypatch) -> None:
    secrets_file = tmp_path / "secrets.json"
    secrets_file.write_text(
        json.dumps({"openai_api_key": "test-key", "tavily_api_key": "", "ollama_api_key": ""}),
        encoding="utf-8",
    )
    monkeypatch.setenv("VAULT_USE_LOCAL", "true")
    client = VaultClient(secret_path="secret/data/test")
    client._local_fallback = secrets_file
    secrets = client.read_secrets()
    assert secrets.openai_api_key == "test-key"