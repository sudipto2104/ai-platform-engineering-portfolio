"""MLflow integration layer for LLM experiment and prompt tracking."""

from __future__ import annotations

import json
import os
import tempfile
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Generator, Optional

import mlflow
from mlflow.tracking import MlflowClient


@dataclass
class LLMRunMetrics:
    relevance_score: Optional[float] = None
    faithfulness_score: Optional[float] = None
    latency_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    extra: dict[str, float] = field(default_factory=dict)

    def to_mlflow_dict(self) -> dict[str, float]:
        metrics: dict[str, float] = {}
        for key, value in asdict(self).items():
            if key == "extra" or value is None:
                continue
            metrics[key] = float(value)
        for key, value in self.extra.items():
            metrics[key] = float(value)
        return metrics


@dataclass
class PromptVersion:
    name: str
    template: str
    model: str
    temperature: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class MLflowLLMTracker:
    """Track prompts, metrics, and artifacts for LLM applications."""

    def __init__(
        self,
        tracking_uri: str | None = None,
        experiment_name: str = "platform-assistant-prompts",
        registry_model_name: str = "platform-assistant-prompt",
    ):
        self.tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        self.experiment_name = experiment_name
        self.registry_model_name = registry_model_name
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment_name)
        self._client = MlflowClient(tracking_uri=self.tracking_uri)

    @contextmanager
    def start_run(
        self,
        run_name: str,
        prompt: PromptVersion | None = None,
        tags: dict[str, str] | None = None,
    ) -> Generator[str, None, None]:
        with mlflow.start_run(run_name=run_name) as run:
            if tags:
                mlflow.set_tags(tags)
            if prompt:
                self.log_prompt(prompt)
            yield run.info.run_id

    def log_prompt(self, prompt: PromptVersion) -> None:
        mlflow.log_param("prompt_name", prompt.name)
        mlflow.log_param("model", prompt.model)
        mlflow.log_param("temperature", prompt.temperature)
        for key, value in prompt.metadata.items():
            mlflow.log_param(f"meta_{key}", value)

        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / f"{prompt.name}.txt"
            prompt_path.write_text(prompt.template, encoding="utf-8")
            mlflow.log_artifact(str(prompt_path), artifact_path="prompts")

            manifest = {
                "name": prompt.name,
                "model": prompt.model,
                "temperature": prompt.temperature,
                "metadata": prompt.metadata,
            }
            manifest_path = Path(tmpdir) / f"{prompt.name}.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            mlflow.log_artifact(str(manifest_path), artifact_path="prompts")

    def log_metrics(self, metrics: LLMRunMetrics) -> None:
        for name, value in metrics.to_mlflow_dict().items():
            mlflow.log_metric(name, value)

    def log_evaluation(
        self,
        prompt: PromptVersion,
        metrics: LLMRunMetrics,
        run_name: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> str:
        run_name = run_name or f"{prompt.name}-{int(time.time())}"
        with self.start_run(run_name=run_name, prompt=prompt, tags=tags) as run_id:
            self.log_metrics(metrics)
        return run_id

    def register_prompt_version(
        self,
        run_id: str,
        version_notes: str = "",
        alias: str | None = "staging",
    ) -> str:
        model_uri = f"runs:/{run_id}/prompts"
        result = mlflow.register_model(model_uri, self.registry_model_name)
        version = result.version

        if version_notes:
            self._client.update_model_version(
                name=self.registry_model_name,
                version=version,
                description=version_notes,
            )

        if alias:
            self._client.set_registered_model_alias(
                name=self.registry_model_name,
                alias=alias,
                version=version,
            )
        return version

    def promote_to_production(self, version: str) -> None:
        self._client.set_registered_model_alias(
            name=self.registry_model_name,
            alias="production",
            version=version,
        )

    def get_production_version(self) -> str | None:
        aliases = self._client.get_registered_model(self.registry_model_name).aliases
        return aliases.get("production")