# Project 06: Platform Engineering Assistant (Capstone)

## Overview

Production-ready AI system integrating **RAG**, **LangGraph agents**, **Kubernetes deployment**, **Prometheus observability**, and **HashiCorp Vault** — the capstone for the AI Infrastructure and MLOps Bootcamp.

## Architecture

```
[User] --> [AI Gateway :8080] --> [Platform Assistant Agent]
                |                         |
                |                         +--> [RAG / ChromaDB]
                |                         +--> [Tools: kubectl, doc search]
                |                         +--> [Guardrails]
                |
                +--> [Prometheus /metrics]
                +--> [Vault Secrets]
```

## Capstone Parts

| Part | Components | Status |
|------|------------|--------|
| **1: RAG Foundation** | ChromaDB, doc ingestion, embeddings, retrieval API | Complete |
| **2: Agent Development** | LangGraph agent, kubectl tools, memory, guardrails | Complete |
| **3: Production Infrastructure** | Helm chart, HPA, health probes, K8s manifests | Complete |
| **4: Observability & Security** | Prometheus, Grafana, Vault, logging, cost tracking | Complete |

## Technologies

| Component | Technology |
|-----------|------------|
| LLM | Ollama (Qwen2.5) |
| Vector DB | ChromaDB |
| Embeddings | Sentence Transformers |
| Agent | LangChain + LangGraph |
| Gateway | FastAPI |
| Orchestration | Kubernetes + Helm |
| Observability | Prometheus + Grafana |
| Secrets | HashiCorp Vault |

## Project Structure

```
06-platform-engineering-assistant/
├── src/platform_assistant/
│   ├── gateway/           # AI Gateway (main entry)
│   ├── agent/             # LangGraph assistant + tools + memory
│   ├── rag/               # Chroma ingestion + retrieval API
│   ├── observability/     # Metrics + structured logging
│   └── security/          # Guardrails + Vault
├── helm/platform-assistant/
├── k8s/                   # Chroma, Vault, namespace
├── prometheus/            # Alert rules
├── grafana/               # Dashboard
├── data/docs/             # Kubernetes documentation
└── scripts/
```

## Quick Start

### 1. Prerequisites

```bash
# Install Ollama and pull the model
ollama pull qwen2.5:3b

# Optional: start Vault dev server
docker run -d --name vault -p 8200:8200 hashicorp/vault:1.17 \
  server -dev -dev-root-token-id=root
```

### 2. Install and test

```bash
cd 06-platform-engineering-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
pytest
```

### 3. Ingest docs and run gateway

```bash
python scripts/ingest_docs.py
python scripts/run_gateway.py
```

### 4. Chat with the assistant

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I troubleshoot CrashLoopBackOff?"}'

curl http://localhost:8080/metrics
```

## Kubernetes Deployment

```bash
# Deploy dependencies
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/chroma.yaml
kubectl apply -f k8s/vault.yaml

# Build and deploy assistant
docker build -t platform-assistant:1.0.0 .
helm install platform-assistant ./helm/platform-assistant \
  -n platform-assistant --create-namespace

kubectl port-forward -n platform-assistant svc/platform-assistant 8080:8080
```

## Success Criteria

| Dimension | Implementation |
|-----------|----------------|
| **Functionality** | RAG-backed K8s answers, read-only kubectl, off-topic refusal, session memory |
| **Reliability** | Health/ready probes, graceful LLM error handling, concurrent FastAPI |
| **Observability** | Prometheus metrics, structured request logging, token/cost tracking |
| **Security** | Vault secrets, input validation, output filtering, command guardrails |

## Verification Checklist

- [ ] `pytest` passes
- [ ] `scripts/ingest_docs.py` indexes documentation
- [ ] `/health` and `/ready` return 200
- [ ] `/metrics` exports Prometheus data
- [ ] Off-topic and dangerous requests are blocked
- [ ] Grafana dashboard imports successfully

## Author

Sudipto Saha — AI Platform Engineering Portfolio