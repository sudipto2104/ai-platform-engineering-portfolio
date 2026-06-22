#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Applying namespace and resource policies..."
kubectl apply -f "${ROOT_DIR}/k8s/namespace.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/resource-quota.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/limit-range.yaml"

echo "Building inference-server image (optional for local clusters)..."
if command -v docker >/dev/null 2>&1; then
  docker build -t inference-server:local "${ROOT_DIR}/inference-server"
fi

echo "Deploying inference workload..."
kubectl apply -f "${ROOT_DIR}/k8s/inference/deployment.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/inference/service.yaml"
kubectl apply -f "${ROOT_DIR}/k8s/inference/pdb.yaml"

echo "Applying VPA recommendation mode (requires VPA CRD)..."
if kubectl api-resources | grep -q verticalpodautoscalers; then
  kubectl apply -f "${ROOT_DIR}/k8s/vpa/vpa-recommendation.yaml"
else
  echo "Skipping VPA: autoscaling.k8s.io/VerticalPodAutoscaler CRD not found."
fi

echo "Done. Port-forward with:"
echo "  kubectl port-forward -n ml-inference svc/inference-server 8080:8080"