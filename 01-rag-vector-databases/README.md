# Project 01: RAG System with Vector Databases

## Overview

Production-ready Retrieval-Augmented Generation (RAG) system with **Chroma** and **pgvector** backends, Kubernetes manifests, and a Helm chart. Forms the foundation of the Platform Assistant knowledge layer.

## Architecture

```
Documents → Token Chunker (600/80) → Embeddings (HuggingFace)
                ↓
        ┌───────┴───────┐
        Chroma      pgvector
        └───────┬───────┘
                ↓
     Hybrid Retrieval (dense + BM25)
                ↓
        RAG Response + Citations
```

## Key Components

- **Ingestion pipeline** — token-based chunking (600 tokens, 80 overlap) with metadata
- **Vector stores** — Chroma (local/server) and pgvector (PostgreSQL extension)
- **Hybrid search** — combines semantic similarity with BM25 keyword scoring
- **RAG pipeline** — retrieval with source citations (`[path#chunk-N]`)
- **Store comparison** — latency and overlap benchmarking between backends
- **Kubernetes** — Chroma and pgvector deployments with persistent storage
- **Helm** — parameterized Chroma chart for cluster deployment

## Technologies

- Chroma / pgvector
- LangChain
- HuggingFace Embeddings (`all-MiniLM-L6-v2`)
- Kubernetes + Helm

## Quick Start (Local)

### 1. Install dependencies

```bash
cd 01-rag-vector-databases
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Ingest sample documents

```bash
python scripts/ingest.py --store chroma
```

### 3. Query with citations

```bash
python scripts/query.py "How does hybrid search work in RAG?"
```

### 4. Run tests

```bash
pytest
```

## pgvector (Optional)

Start PostgreSQL with pgvector:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/pgvector/postgres.yaml
```

Port-forward and ingest:

```bash
kubectl port-forward -n rag-system svc/pgvector 5432:5432
python scripts/ingest.py --store pgvector
python scripts/compare_stores.py "vector database comparison"
```

## Kubernetes Deployment

```bash
# Raw manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/chroma/

# Or Helm
helm install chroma ./helm/chroma -n rag-system --create-namespace
```

## Project Structure

```
01-rag-vector-databases/
├── src/rag_system/       # Core library
├── scripts/              # CLI tools (ingest, query, compare)
├── data/sample_docs/     # Sample knowledge base
├── k8s/                  # Kubernetes manifests
├── helm/chroma/          # Helm chart
├── config/settings.yaml  # Default configuration
└── tests/
```

## Configuration

Copy `.env.example` to `.env` to override defaults:

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | 600 | Tokens per chunk |
| `CHUNK_OVERLAP` | 80 | Overlap between chunks |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | HuggingFace model |
| `CHROMA_PERSIST_DIR` | ./data/chroma | Local Chroma storage |
| `COLLECTION_NAME` | platform_docs | Chroma collection |

## Author

Sudipto Saha — AI Platform Engineering Portfolio