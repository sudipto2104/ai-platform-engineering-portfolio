from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os

load_dotenv()

# Load embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="platform_knowledge"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# Prompt
template = """You are a helpful Platform Engineering Assistant.
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know.

Context: {context}

Question: {question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)

# LLM
llm = ChatOllama(
    model="llama3.2",
    temperature=0.3,
)

# RAG Chain
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Test function
def ask_question(question: str):
    print(f"\n❓ Question: {question}")
    response = rag_chain.invoke(question)
    print(f"💡 Answer: {response}")
    return response

if __name__ == "__main__":
    print("✅ RAG Chain loaded successfully!")
    ask_question("What is the purpose of this RAG system?")
