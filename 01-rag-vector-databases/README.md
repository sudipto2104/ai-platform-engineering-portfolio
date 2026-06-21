# 🤖 Platform Engineering Assistant

An intelligent RAG-based assistant that helps Platform Engineers quickly find answers from internal documentation and best practices.

## 🚀 Features

- Ask questions about Kubernetes, Cilium, Platform Engineering, GitOps, etc.
- Retrieves relevant context before answering (RAG)
- Clean chat interface built with Gradio
- Powered by OpenAI

## 🛠 Tech Stack

- **LLM**: OpenAI (`gpt-4o-mini`)
- **Embeddings**: OpenAI (`text-embedding-3-small`)
- **Vector Store**: Chroma
- **Framework**: LangChain
- **UI**: Gradio

## 🎯 Live Demo (https://colab.research.google.com/github/sudipto2104/ai-platform-engineering-portfolio/blob/main/01-rag-vector-databases/01_rag_openai_colab.ipynb)

> Click the button above to open and run the demo

## How to Run Locally

```bash
cd 01-rag-vector-databases
pip install -r requirements.txt
python -m gradio ui_gradio.py
