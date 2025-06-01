import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.config import VECTOR_DB_DIR
from src.embedding_model import get_embedding_model

def get_vector_store():
    """Initializes and returns the Chroma vector store."""
    embedding_model = get_embedding_model()
    # If the directory exists, it will try to load the existing collection
    # Otherwise, it will create a new one when documents are added
    vector_store = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embedding_model
    )
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