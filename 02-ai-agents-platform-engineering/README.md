# Project 02: AI Agent using LangGraph

An intelligent AI Agent built using LangGraph that can reason, use tools, and complete complex tasks.

## 🚀 Features

- Ask questions and get intelligent answers with reasoning.
- Tool use capability via Web Search for up-to-date information or facts.
- Built using the ReAct pattern.
- Easy to run terminal interface.

## 🛠 Tech Stack

- **LLM**: OpenAI (`gpt-4o-mini`)
- **Tools**: Tavily Search
- **Framework**: LangChain, LangGraph

## How to Run Locally

```bash
cd 02-ai-agents-platform-engineering
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and TAVILY_API_KEY
python test_agent.py
```
