# Project 03: MLflow for LLMOps

## Overview

Production-grade **MLflow** deployment for tracking LLM experiments, prompts, evaluation metrics, and token usage. PostgreSQL stores metadata; MinIO provides S3-compatible artifact storage.

## Architecture

```
LLM Application
      ↓
MLflowLLMTracker (integration layer)
      ↓
MLflow Tracking Server (Kubernetes)
      ├── PostgreSQL  (metadata / experiments)
      └── MinIO       (prompt artifacts, eval outputs)
```

## Key Components

- MLflow Tracking Server on Kubernetes
- PostgreSQL backend for experiment metadata
- MinIO (S3-compatible) for artifact storage
- `MLflowLLMTracker` integration layer for prompt versioning and metrics
- Model Registry support with staging/production aliases

## Project Structure

```
03-mlflow-llmops/
├── README.md
├── requirements.txt
├── pyproject.toml
├── mlflow-kubernetes-deployment/
│   ├── namespace.yaml
│   ├── postgres.yaml
│   ├── minio.yaml
│   └── mlflow.yaml
├── mlflow-integration/
│   └── mlflow_tracker.py
├── scripts/
│   └── example_tracking.py
└── tests/
    └── test_mlflow_tracker.py
```

## Deployment (Kubernetes)

```bash
kubectl apply -f mlflow-kubernetes-deployment/
```

Wait for pods to become ready:

```bash
kubectl get pods -n mlflow -w
```

Access MLflow UI:

```bash
kubectl port-forward svc/mlflow 5000:5000 -n mlflow
```

Open [http://localhost:5000](http://localhost:5000).

## Local Development

```bash
cd 03-mlflow-llmops
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

With MLflow running (port-forward or local server):

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
python scripts/example_tracking.py
```

## Integration Example

```python
from mlflow_tracker import LLMRunMetrics, MLflowLLMTracker, PromptVersion

tracker = MLflowLLMTracker(tracking_uri="http://localhost:5000")

prompt = PromptVersion(
    name="platform-assistant-v1.3",
    template="Use context to answer: {question}",
    model="gpt-4o-mini",
    temperature=0.1,
)

metrics = LLMRunMetrics(
    relevance_score=4.6,
    faithfulness_score=4.8,
    input_tokens=1240,
    output_tokens=186,
    cost_usd=0.00034,
)

run_id = tracker.log_evaluation(prompt=prompt, metrics=metrics, run_name="prompt-v1.3")
version = tracker.register_prompt_version(run_id, alias="staging")
tracker.promote_to_production(version)
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow server URL |
| `MLFLOW_EXPERIMENT_NAME` | `platform-assistant-prompts` | Experiment name |
| `MLFLOW_REGISTRY_MODEL_NAME` | `platform-assistant-prompt` | Registry model |

## Why This Matters

- Treat prompts as first-class, versioned artifacts
- Compare prompt versions objectively using metrics
- Enable safe rollback using MLflow Model Registry aliases
- Bring engineering discipline to prompt engineering

## Author

Built as part of an AI Platform Engineering portfolio by Sudipto Saha.