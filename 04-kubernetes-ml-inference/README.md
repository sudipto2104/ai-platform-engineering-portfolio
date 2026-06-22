# Project 04: Kubernetes Resource Management for ML Inference

## Overview

Production patterns for running ML inference workloads on Kubernetes with fair resource allocation, predictable QoS, right-sizing workflows, and safe disruption handling.

## Architecture

```
Namespace (ml-inference)
├── ResourceQuota     → cluster fairness (CPU, memory, GPU)
├── LimitRange        → per-pod defaults and boundaries
├── Inference Deployment (Guaranteed QoS)
├── PodDisruptionBudget
└── VPA (recommendation mode)
         ↓
measure_workload.py → analyze_rightsizing.py
```

## Key Topics Covered

- **ResourceQuotas** — cap CPU, memory, GPU, and pod count per namespace
- **LimitRanges** — enforce container defaults, min/max boundaries
- **QoS classes** — Guaranteed, Burstable, and BestEffort reference manifests
- **Right-sizing** — measure latency under load and recommend requests/limits
- **VPA** — recommendation-only mode for safe resource tuning
- **Pod Disruption Budgets** — maintain availability during node drains

## Project Structure

```
04-kubernetes-ml-inference/
├── k8s/
│   ├── namespace.yaml
│   ├── resource-quota.yaml
│   ├── limit-range.yaml
│   ├── inference/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── pdb.yaml
│   │   └── qos-examples.yaml
│   └── vpa/
│       └── vpa-recommendation.yaml
├── inference-server/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── scripts/
│   ├── deploy.sh
│   ├── measure_workload.py
│   └── analyze_rightsizing.py
├── config/
│   └── workload-profiles.yaml
└── tests/
```

## Quick Start

### 1. Install dependencies

```bash
cd 04-kubernetes-ml-inference
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### 2. Deploy to Kubernetes

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 3. Port-forward and measure

```bash
kubectl port-forward -n ml-inference svc/inference-server 8080:8080

python scripts/measure_workload.py --requests 100 --concurrency 8
python scripts/analyze_rightsizing.py
```

## QoS Classes

| Class | When to use | Configuration |
|-------|-------------|---------------|
| **Guaranteed** | Production inference, predictable memory | `requests == limits` |
| **Burstable** | Dev/test, variable CPU bursts | `requests < limits` |
| **BestEffort** | Batch/offline only (not recommended for serving) | no requests/limits |

See `k8s/inference/qos-examples.yaml` for side-by-side manifests.

## VPA Recommendations

VPA runs in `updateMode: Off` (recommendations only). View suggestions:

```bash
kubectl describe vpa inference-server-vpa -n ml-inference
```

Requires the [Vertical Pod Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler) CRD.

## Workload Profiles

`config/workload-profiles.yaml` defines `small`, `medium`, and `large` inference profiles with headroom multipliers for right-sizing analysis.

## Why It Matters

Inference workloads have unique characteristics — bursty CPU, predictable memory, and slow cold starts. Proper resource configuration prevents OOM kills, ensures fairness across teams, and improves reliability during cluster maintenance.

## Author

Sudipto Saha — AI Platform Engineering Portfolio