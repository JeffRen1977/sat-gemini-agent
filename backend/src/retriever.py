from langchain_core.retrievers import BaseRetriever
from src.vector_store import get_vector_store
from src.config import TOP_K_RETRIEVAL

def get_retriever() -> BaseRetriever:
    """Configures and returns the retriever."""
    vector_store = get_vector_store()
    # You can choose different search types: "similarity", "mmr" (Maximum Marginal Relevance)
    # "mmr" tries to balance similarity with diversity, which can be useful.
    retriever = vector_store.as_retriever(
        search_type="similarity", # or "mmr"
        search_kwargs={"k": TOP_K_RETRIEVAL}
    )
    print(f"Retriever configured to fetch {TOP_K_RETRIEVAL} documents.")
    return retriever