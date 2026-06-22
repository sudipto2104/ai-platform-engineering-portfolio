# Project 02: AI Agents for Platform Engineering

## Overview

Production-grade AI agents for platform engineering — Kubernetes troubleshooting, safe tool execution, human-in-the-loop approvals, MCP tool serving, and multi-agent supervisor routing.

## Architecture

```
User Query
    ↓
Supervisor Agent ──→ Kubernetes Specialist (get_pods, logs, describe)
    │              └──→ Search Specialist (Tavily)
    ↓
Guardrails + Approval Gate
    ↓
MCP Server (standardized tool interface)
```

## Agents Included

| Agent | Description |
|-------|-------------|
| **ReAct Agent** | Basic reasoning + Tavily web search |
| **Platform Assistant** | K8s tools with guardrails |
| **Approval Workflow** | Human-in-the-loop for dangerous ops |
| **MCP Server** | FastAPI server exposing K8s tools via MCP/REST |
| **Supervisor** | Routes queries to Kubernetes or search specialists |

## Key Features

- Safe tool execution with guardrails (blocks delete/drain/exec)
- Human approval for write operations (`AUTO_APPROVE` for CI)
- Standardized tool interface via MCP JSON-RPC + REST
- Supervisor routing for complex tasks
- Dry-run Kubernetes mode for local dev (`K8S_DRY_RUN=true`)

## Project Structure

```
02-ai-agents-platform-engineering/
├── src/platform_agents/
│   ├── react_agent.py
│   ├── platform_assistant.py
│   ├── supervisor.py
│   └── tools/
├── mcp_server/
├── scripts/
├── k8s/
├── tests/
├── agent.py                  # backward-compatible entrypoint
└── 02-langgraph-ai-agent.ipynb
```

## Quick Start

### 1. Install

```bash
cd 02-ai-agents-platform-engineering
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### 2. Run tests (no API keys required)

```bash
pytest
```

### 3. Run agents

```bash
# Basic ReAct agent (requires OPENAI_API_KEY + TAVILY_API_KEY)
python scripts/run_react_agent.py "What is GitOps?"

# Platform assistant with K8s tools (dry-run mode)
python scripts/run_platform_assistant.py "Which pods are running in default?"

# Multi-agent supervisor
python scripts/run_supervisor.py "Why is my pod CrashLoopBackOff?"

# MCP server
python scripts/run_mcp_server.py
curl http://localhost:8090/tools
```

### 4. Deploy MCP server to Kubernetes

```bash
docker build -t platform-mcp-server:local .
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mcp-server.yaml
kubectl port-forward -n platform-agents svc/mcp-server 8090:8090
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | OpenAI API key |
| `TAVILY_API_KEY` | — | Tavily search API key |
| `K8S_DRY_RUN` | `true` | Mock K8s tool output locally |
| `AUTO_APPROVE` | `false` | Skip human approval prompts |
| `MCP_PORT` | `8090` | MCP server port |

## Integration Example

```python
from platform_agents.platform_assistant import ask_platform_assistant
from platform_agents.tools.approval import ApprovalGate

gate = ApprovalGate(auto_approve=False)
answer = ask_platform_assistant(
    "Show me pods in default and explain any failures",
    approval_gate=gate,
)
```

## Live Demo

[Open the Colab notebook](https://colab.research.google.com/github/sudipto2104/ai-platform-engineering-portfolio/blob/main/02-ai-agents-platform-engineering/02-langgraph-ai-agent.ipynb)

## Author

Sudipto Saha — AI Platform Engineering Portfolio