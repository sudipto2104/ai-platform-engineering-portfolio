from agent import ask_agent

print("🤖 AI Agent Test\n")

questions = [
    "Who is the current CEO of OpenAI?",
    "What are the latest developments in Kubernetes in 2026?",
    "What is the difference between ArgoCD and Flux?"
]

for question in questions:
    ask_agent(question)

print("✅ Test completed!")
