import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# --- Paths ---
DATA_RAW_DIR = "data/raw"
VECTOR_DB_DIR = "vector_db/chroma_db"

# --- Embedding Model ---
# For local models (e.g., from Hugging Face)
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
# For OpenAI embeddings:
# EMBEDDING_MODEL_NAME = "text-embedding-3-small"

# For Google AI Studio / Gemini API embeddings:
EMBEDDING_MODEL_NAME = "models/embedding-001" # Or "models/text-embedding-004"
# For Google Cloud Vertex AI embeddings (requires specific GCP setup):
# EMBEDDING_MODEL_NAME = "text-embedding-preview-0409" # Example Vertex AI model

# --- LLM Model ---
#LLM_MODEL_NAME = "models/gemini-2.5-flash-preview-05-20" # Or "gpt-3.5-turbo", "gemini-pro", "llama3", etc.

# --- Chunking Parameters ---
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200 # Overlap between chunks

# --- Retrieval Parameters ---
TOP_K_RETRIEVAL = 5 # Number of relevant documents to retrieve