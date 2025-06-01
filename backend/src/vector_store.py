# sat_gemini_agent/backend/src/vector_store.py
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.config import VECTOR_DB_DIR
from src.embedding_model import get_embedding_model
import os # Import os to check directory existence

def get_vector_store():
    """Initializes and returns the Chroma vector store."""
    embedding_model = get_embedding_model()

    # Check if the persist_directory exists and contains data
    if os.path.exists(VECTOR_DB_DIR) and len(os.listdir(VECTOR_DB_DIR)) > 0:
        print(f"Loading existing ChromaDB from: {VECTOR_DB_DIR}")
        vector_store = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embedding_model
        )
        # Add a print to show the count of documents
        count = vector_store._collection.count()
        print(f"ChromaDB loaded. It contains {count} documents.")
        if count == 0:
            print("WARNING: The loaded ChromaDB is empty. You might need to run an ingestion script.")
    else:
        print(f"ChromaDB directory not found or is empty at: {VECTOR_DB_DIR}. Initializing new ChromaDB.")
        vector_store = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embedding_model
        )
        print("New empty ChromaDB initialized. You need to add documents to it.")

    return vector_store

def add_documents_to_vector_store(chunks: list[Document]):
    """Adds a list of LangChain Documents (chunks) to the vector store."""
    vector_store = get_vector_store()
    # Check if chunks are already in the store (simple check based on count)
    # A more robust check might involve comparing chunk IDs or hashes
    if vector_store._collection.count() == 0:
        print(f"Adding {len(chunks)} chunks to the vector store...")
        vector_store.add_documents(chunks)
        print("Documents added successfully.")
    else:
        print(f"Vector store already contains {vector_store._collection.count()} documents. Skipping addition.")
        print("To re-ingest, delete the 'vector_db/chroma_db' directory and run ingest.py again.")