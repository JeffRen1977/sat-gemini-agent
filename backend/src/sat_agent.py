# src/sat_agent.py
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.llm_model import get_llm_model
from src.retriever import get_retriever
from src.prompt_templates import SAT_RAG_PROMPT

def create_sat_rag_agent():
    llm = get_llm_model()
    retriever = get_retriever()

    document_combiner = create_stuff_documents_chain(
        llm,
        SAT_RAG_PROMPT,
        document_variable_name="context"
    )

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | document_combiner
        | StrOutputParser()
    )

    print("SAT RAG Agent pipeline created successfully.")
    return rag_chain