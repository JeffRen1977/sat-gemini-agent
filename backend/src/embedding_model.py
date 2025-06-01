# sat_gemini_agent/backend/src/embedding_model.py
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.config import EMBEDDING_MODEL_NAME
import os

def get_embedding_model():
    """Initializes and returns the chosen embedding model."""
    if "bge" in EMBEDDING_MODEL_NAME.lower() or "minilm" in EMBEDDING_MODEL_NAME.lower():
        return HuggingFaceBgeEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    elif "text-embedding" in EMBEDDING_MODEL_NAME.lower() and "openai" in EMBEDDING_MODEL_NAME.lower():
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set in .env for OpenAI embeddings.")
        return OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    elif "models/embedding" in EMBEDDING_MODEL_NAME.lower() or "models/text-embedding" in EMBEDDING_MODEL_NAME.lower():
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not set in .env for Google embeddings.")
        
        return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME, google_api_key=google_api_key)
    else:
        raise ValueError(f"Unsupported embedding model: {EMBEDDING_MODEL_NAME}")