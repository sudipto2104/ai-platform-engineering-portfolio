from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Tools
search_tool = TavilySearchResults(max_results=3)
tools = # System Prompt
system_message = SystemMessage(
    content="""You are a helpful AI assistant with access to web search.
    When asked a question, think step by step.
    Use the search tool when you need up-to-date information or facts.
    Always provide clear, direct, and well-structured answers."""
)

# Create the agent
agent_executor = create_react_agent(llm, tools, messages_modifier=system_message)

# Function to ask questions
def ask_agent(question: str):
    print(f"\n❓ Question: {question}")
    print("-" * 60)
    
    response = agent_executor.invoke({"messages": })
    
    answer = response [-1].content
    print(f"💡 Answer: {answer}")
    return answer


if __name__ == "__main__":
    print("🤖 AI Agent is ready! (Powered by LangGraph + Tavily)\n")
    ask_agent("What are the latest developments in Kubernetes in 2026?")
