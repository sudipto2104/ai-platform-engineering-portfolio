# 01 - RAG System with Vector Databases

Production-ready Retrieval Augmented Generation system for Platform Engineering knowledge.

## Features
- Support for both **pgvector (Supabase)** and **Chroma**
- Smart document chunking (600 tokens with 80 overlap)
- Rich metadata handling
- Source citations in responses
- FastAPI backend + Gradio UI
- Built for cloud development (GitHub Codespaces + Supabase)

## Tech Stack
- LangChain
- pgvector / Chroma
- HuggingFace Embeddings
- FastAPI + Gradio

## Quick Start

1. Copy `.env.example` to `.env` and update values
2. `pip install -r requirements.txt`
3. Run ingestion: `python ingestion.py`
4. Run UI: `python ui_gradio.py`

## Project Structure
- `ingestion.py` - Document processing and vector store ingestion
- `rag_chain.py` - Core RAG pipeline with citations
- `rag_api.py` - FastAPI backend
- `ui_gradio.py` - Interactive demo UI
