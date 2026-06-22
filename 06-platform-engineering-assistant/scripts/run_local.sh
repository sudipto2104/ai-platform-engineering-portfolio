#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

source .venv/bin/activate 2>/dev/null || true

echo "Ingesting documentation..."
python scripts/ingest_docs.py

echo "Starting Platform Engineering Assistant gateway..."
export K8S_DRY_RUN=true
export VAULT_USE_LOCAL=true
python scripts/run_gateway.py