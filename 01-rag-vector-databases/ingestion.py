import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# ================= CONFIG =================
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ================= LOAD DOCUMENTS =================
def load_documents(doc_dir="docs"):
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir, exist_ok=True)
        print(f"📁 Created '{doc_dir}' folder. Put your PDF, TXT, MD files here.")
        return []

    print(f"📄 Loading documents from '{doc_dir}' folder...")

    documents = []

    # Load PDFs
    pdf_loader = DirectoryLoader(doc_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents.extend(pdf_loader.load())

    # Load Text & Markdown files
    text_loader = DirectoryLoader(
        doc_dir, 
        glob="**/*.{txt,md}", 
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents.extend(text_loader.load())

    print(f"✅ Loaded {len(documents)} documents")
    return documents


# ================= MAIN =================
def main():
    print("🚀 RAG Ingestion Pipeline Started\n")

    documents = load_documents()

    if not documents:
        print("❌ No documents found!")
        return

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    splits = text_splitter.split_documents(documents)
    print(f"✂️  Created {len(splits)} chunks")

    # Create vector store using Chroma
    print("💾 Creating Chroma vector database...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./chroma_db",
        collection_name="platform_knowledge"
    )

    print("\n🎉 Ingestion Completed Successfully!")
    print(f"✅ {len(splits)} chunks saved in './chroma_db' folder")

if __name__ == "__main__":
    main()
