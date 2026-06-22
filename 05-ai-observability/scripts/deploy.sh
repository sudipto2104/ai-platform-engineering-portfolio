#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

kubectl apply -f "${ROOT_DIR}/k8s/namespace.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/deployment.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/service.yaml"

if kubectl api-resources | grep -q servicemonitors; then
  kubectl apply -f "${ROOT_DIR}/k8s/servicemonitor.yaml"
else
  echo "Skipping ServiceMonitor: monitoring.coreos.com CRD not found."
fi

if command -v docker >/dev/null 2>&1; then
  docker build -t llm-metrics-exporter:local "${ROOT_DIR}/observability-layer"
fi

echo "Port-forward metrics with:"
echo "  kubectl port-forward -n ai-observability svc/llm-metrics-exporter 8000:8000"