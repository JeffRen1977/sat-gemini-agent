## Backend Architecture Overview

This document outlines the architecture of the backend system, focusing on its core components and their interactions.

### Flask Application (`app.py`)

The backend is built using the Flask framework. `app.py` serves as the main entry point and is responsible for:

- **Initialization**: Setting up the Flask application instance.
- **Configuration**: Loading application configurations, including database URIs and API keys.
- **Blueprints & Routing**: While not explicitly detailed in the provided `app.py` snippet, a typical Flask structure would involve Blueprints for organizing routes. `app.py` would register these Blueprints to handle incoming HTTP requests for different API endpoints (e.g., `/chat`, `/submit_answer`).
- **Request Handling**: Defining functions that are executed when specific API endpoints are accessed. These functions process incoming data (e.g., user queries, answers) and orchestrate responses.
- **Error Handling**: Implementing mechanisms to catch and manage errors gracefully.
- **CORS**: The application uses `flask_cors` to handle Cross-Origin Resource Sharing, allowing requests from different domains (likely the frontend application).

### Data Persistence (SQLAlchemy & `models.py`)

The application utilizes SQLAlchemy as an Object-Relational Mapper (ORM) to interact with a relational database (likely PostgreSQL or SQLite based on common Flask practices, though not explicitly stated). The database models are defined in `models.py`:

- **`User` Model**: Represents users of the application. It likely stores user identifiers and potentially authentication-related information.
- **`QuestionAttempt` Model**: Tracks user attempts at answering questions. This model would store details such as the question asked, the user's answer, whether the answer was correct, and any feedback provided.

SQLAlchemy allows the application to manage database records as Python objects, simplifying database operations like creating, reading, updating, and deleting (CRUD) data.

### AI Logic Hub (`GeminiService` in `gemini_service.py`)

The `GeminiService` class is the central component for handling all AI-powered functionalities. Its primary responsibilities include:

- **Interfacing with Google's Generative AI**: It uses the `google.generativeai` library to connect to and interact with Google's large language models (LLMs), specifically a "gemini-pro" model.
- **Chat Functionality**: The `chat_with_gemini` method takes a user's message and conversation history to generate contextually relevant responses from the LLM. It manages the conversation flow and safety settings for the AI model.
- **Answer Evaluation**: The `evaluate_answer` method is crucial for the quiz/learning aspect of the application. It takes a question, the user's answer, and relevant context (retrieved by the `retriever`) to determine if the answer is correct. It likely formulates a prompt to the LLM to perform this evaluation.
- **Prompt Engineering**: While not explicitly shown in detail, `GeminiService` is implicitly responsible for constructing effective prompts to guide the LLM's behavior for both chat and answer evaluation.

### Contextual Information Retrieval (`retriever` component)

The `GeminiService` utilizes a `retriever` component to fetch relevant contextual information. Based on common patterns in RAG (Retrieval Augmented Generation) architectures:

- **Vector Database**: The `retriever` most likely interacts with a vector database (e.g., ChromaDB, FAISS, Pinecone). This database would store embeddings (vector representations) of text chunks from a knowledge base (e.g., course materials, documentation).
- **Similarity Search**: When a user asks a question or submits an answer, the `retriever` converts the query/question into an embedding and performs a similarity search in the vector database to find the most relevant text chunks.
- **Augmenting Prompts**: The retrieved context is then passed to the `GeminiService`, which includes it in the prompt sent to the LLM. This allows the LLM to generate more informed and accurate responses or evaluations. The `get_relevant_documents` method in the `retriever` (as hinted by its usage in `evaluate_answer`) is responsible for this retrieval process.

In summary, the backend combines a Flask web framework for API handling, SQLAlchemy for database interactions, and the `GeminiService` as the core AI engine. The `GeminiService` leverages Google's generative AI models and a `retriever` (likely a vector database) to provide intelligent chat and answer evaluation capabilities.
