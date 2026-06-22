# Project 05: AI Observability for LLM Systems

## Overview

Production-grade observability layer for LLM-powered applications. Tracks token usage, cost attribution, latency decomposition (TTFT, generation, total), guardrails, user feedback, and LLM-as-judge evaluation scores via Prometheus.

## Architecture

```
LLM Application
      ↓
ai_observability.py  (metrics + track_llm_call wrapper)
      ↓
evaluator.py         (LLM-as-judge quality scores)
      ↓
metrics_server.py    (/metrics exporter)
      ↓
Prometheus → Grafana dashboards + alerts
```

## Key Features

- Prometheus metrics for tokens, cost, latency, and quality
- `track_llm_call` context manager with TTFT support
- Cost attribution by model and feature
- Guardrail and user feedback tracking
- LLM-as-judge evaluation framework
- Kubernetes deployment + ServiceMonitor
- Grafana dashboard and Prometheus alert rules

## Project Structure

```
05-ai-observability/
├── observability-layer/
│   ├── ai_observability.py
│   ├── evaluator.py
│   ├── metrics_server.py
│   ├── example_usage.py
│   └── Dockerfile
├── k8s/
├── prometheus/
├── grafana/
├── scripts/
└── tests/
```

## Quick Start

### 1. Install and test

```bash
cd 05-ai-observability
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### 2. Run locally

Terminal 1 — start metrics server:

```bash
cd observability-layer
python metrics_server.py
```

Terminal 2 — generate sample metrics:

```bash
python scripts/run_demo.py
```

Scrape: [http://localhost:8000/metrics](http://localhost:8000/metrics)

### 3. Deploy to Kubernetes

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
kubectl port-forward -n ai-observability svc/llm-metrics-exporter 8000:8000
```

## Metrics Exposed

| Metric | Description | Labels |
|--------|-------------|--------|
| `llm_requests_total` | Total LLM requests | model, status, request_type |
| `llm_tokens_total` | Token usage | model, token_type, request_type |
| `llm_tokens_per_request` | Token distribution | model, token_type |
| `llm_latency_seconds` | Latency breakdown | model, phase (ttft, generation, total) |
| `llm_cost_dollars_total` | Cost in USD | model, feature |
| `llm_evaluation_score` | LLM-as-judge scores | model, metric_name, evaluator |
| `guardrail_triggers_total` | Safety filter triggers | guardrail_type, action |
| `user_feedback_total` | User feedback signals | feedback_type, sentiment |

## Integration Example

```python
from ai_observability import track_llm_call, record_tokens, record_cost, record_ttft
from evaluator import EvaluationInput, LLMJudgeEvaluator

with track_llm_call(model="gpt-4o-mini", request_type="rag", feature="platform_assistant") as call:
    # first token received
    call.mark_first_token()
    response = llm_client.chat(...)
    record_tokens("gpt-4o-mini", input_tokens, output_tokens, "rag")
    record_cost("gpt-4o-mini", cost, feature="platform_assistant")

evaluator = LLMJudgeEvaluator()
evaluator.evaluate_and_record(EvaluationInput(question=q, answer=response, context=ctx))
```

## Dashboards and Alerts

- Import `grafana/llm-observability-dashboard.json` into Grafana
- Apply `prometheus/alert-rules.yaml` for cost spikes, error rates, latency, and quality degradation
- Use `prometheus/scrape-config.yaml` as a reference scrape job

## Production Recommendations

- Run the metrics exporter as a sidecar or shared cluster service
- Combine with OpenTelemetry for distributed tracing
- Replace heuristic evaluator with a real LLM-as-judge pipeline in production
- Alert on cost, error rate, p95 latency, and evaluation score drops

## Author

Built as part of an AI Platform Engineering portfolio by Sudipto Saha.