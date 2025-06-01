# sat_gemini_agent/backend/src/llm_model.py
from langchain_openai import ChatOpenAI
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import LLM_MODEL_NAME
import os

def get_llm_model():
    """Initializes and returns the chosen LLM."""
    if "gpt" in LLM_MODEL_NAME.lower():
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set in .env for OpenAI LLM.")
        return ChatOpenAI(model=LLM_MODEL_NAME, temperature=0.3)
    elif "gemini" in LLM_MODEL_NAME.lower():
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not set in .env for Google LLM.")
        
        return ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=0.3, google_api_key=google_api_key)
    else:
        raise ValueError(f"Unsupported LLM model: {LLM_MODEL_NAME}")