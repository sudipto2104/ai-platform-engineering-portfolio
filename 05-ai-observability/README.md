# Project 05: AI Observability for LLM Systems

## Overview

This project implements a production-grade observability layer for LLM-powered applications, following best practices from modern LLMOps.

It captures the metrics that actually matter for AI systems:
- Token usage and cost
- Latency breakdown (including Time to First Token)
- Quality and safety signals (guardrails, user feedback)
- Model-level metadata

## Key Features

- Prometheus metrics for tokens, cost, latency, and quality
- Easy-to-integrate wrapper for LLM calls
- Support for cost attribution by model and feature
- Latency decomposition (TTFT, generation, total)
- Guardrail and user feedback tracking
- Ready for Grafana dashboards

## Project Structure

```
05-ai-observability/
├── README.md
└── observability-layer/
    ├── ai_observability.py      # Core metrics and wrapper
    ├── metrics_server.py        # Prometheus exporter
    └── example_usage.py         # Integration example
```

## Setup

```bash
cd 05-ai-observability/observability-layer
pip install prometheus-client
```

## Quick Start

1. Start the metrics server:
```bash
python metrics_server.py
```

2. Integrate into your application (see `example_usage.py`)

3. Scrape metrics from `http://localhost:8000/metrics`

## Metrics Exposed

| Metric | Description | Labels |
|--------|-------------|--------|
| `llm_requests_total` | Total LLM requests | model, status, request_type |
| `llm_tokens_total` | Token usage | model, token_type, request_type |
| `llm_latency_seconds` | Latency breakdown | model, phase |
| `llm_cost_dollars_total` | Cost in USD | model, feature |
| `guardrail_triggers_total` | Safety filter triggers | guardrail_type, action |
| `user_feedback_total` | User feedback signals | feedback_type, sentiment |

## Integration Example

```python
from ai_observability import track_llm_call, record_tokens, record_cost

with track_llm_call(model="gpt-4o-mini", request_type="rag"):
    response = llm_client.chat(...)
    record_tokens("gpt-4o-mini", input_tokens, output_tokens, "rag")
    record_cost("gpt-4o-mini", cost, feature="platform_assistant")
```

## Production Recommendations

- Run `metrics_server.py` as a sidecar or separate deployment
- Create Grafana dashboards for Cost, Tokens, Latency, and Quality
- Set up alerts for cost spikes and quality degradation
- Combine with OpenTelemetry for full distributed tracing

## Author

Built as part of an AI Platform Engineering portfolio by Sudipto Saha.