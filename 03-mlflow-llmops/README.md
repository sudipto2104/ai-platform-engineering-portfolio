# Project 03: MLflow for LLMOps

## Overview

This project demonstrates how to deploy and use **MLflow** as a central experiment tracking and model registry system for LLM applications.

It follows production best practices for LLMOps, enabling teams to track prompts, evaluation scores, token usage, and promote successful prompt versions.

## Key Components

- Production-grade MLflow Tracking Server on Kubernetes
- PostgreSQL backend for metadata
- MinIO (S3-compatible) for artifact storage
- Integration layer for logging LLM experiments

## Project Structure

```
03-mlflow-llmops/
├── README.md
├── mlflow-kubernetes-deployment/
│   ├── postgres.yaml
│   ├── minio.yaml
│   └── mlflow.yaml
└── mlflow-integration/
    └── mlflow_tracker.py
```

## Deployment (Kubernetes)

```bash
kubectl apply -f mlflow-kubernetes-deployment/
```

Access MLflow UI:
```bash
kubectl port-forward svc/mlflow 5000:5000 -n mlflow
```

## Integration Example

```python
import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("platform-assistant-prompts")

with mlflow.start_run(run_name="prompt-v1.3"):
    mlflow.log_param("model", "gpt-4o-mini")
    mlflow.log_param("temperature", 0.1)
    mlflow.log_metric("relevance_score", 4.6)
    mlflow.log_metric("faithfulness_score", 4.8)
```

## Why This Matters

- Treat prompts as first-class, versioned artifacts
- Compare prompt versions objectively using metrics
- Enable safe rollback using MLflow Model Registry aliases
- Bring engineering discipline to prompt engineering

## Author

Built as part of an AI Platform Engineering portfolio by Sudipto Saha.