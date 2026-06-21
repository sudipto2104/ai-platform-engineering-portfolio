from ingestion import main as ingest
from rag_chain import ask_question

print("=== Platform Engineering RAG System ===\n")

print("1. Running Ingestion...")
ingest()

print("\n2. Testing RAG System...")
ask_question("What is Kubernetes Network Policy?")
ask_question("Why do we use Cilium?")

print("\n✅ Setup completed! Now you can run:")
print("   python -m gradio ui_gradio.py")
