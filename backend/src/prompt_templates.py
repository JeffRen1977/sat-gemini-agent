from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# System prompt sets the persona and overall instructions for the LLM
SYSTEM_PROMPT = """You are an expert SAT test preparation assistant. Your goal is to help students understand and answer SAT questions.
Use the following context to answer the user's question.
If the context does not contain enough information to answer the question, politely state that you cannot answer based on the provided information.
Provide clear, step-by-step explanations for the correct answer.
For incorrect options, briefly explain why they are wrong if possible and relevant to the context.
Ensure your response is directly relevant to the SAT exam format and content.
Do not hallucinate or provide information not supported by the context.

Context:
{context}
"""

# Human (user) prompt is the actual question from the student
HUMAN_PROMPT = """
SAT Question: {question} # <--- THIS IS KEY
Please provide the correct answer and a detailed explanation, referencing the provided context.
"""

# Combine into a ChatPromptTemplate
SAT_RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])

# For conversational memory (optional, if you expand beyond single-turn Q&A)
# CONVERSATIONAL_RAG_PROMPT = ChatPromptTemplate.from_messages([
#     ("system", SYSTEM_PROMPT),
#     MessagesPlaceholder("chat_history"), # For conversational memory
#     ("human", HUMAN_PROMPT),
# ])