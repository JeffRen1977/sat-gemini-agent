## Overall System Architecture

This application is a full-stack system designed to provide an AI-powered learning and assessment experience. It comprises several key components that work together:

1.  **Frontend (React)**:
    *   **Role:** Serves as the primary user interface (UI).
    *   **Responsibilities:** Renders web pages, captures user input (answers, topic selections, image uploads), manages client-side state, and displays information received from the backend. It is likely located in the `frontend/` directory.

2.  **Backend (Flask)**:
    *   **Role:** Acts as the central nervous system of the application.
    *   **Responsibilities:**
        *   Exposes a RESTful API for the frontend to consume.
        *   Handles incoming HTTP requests and routes them to appropriate controllers or service functions.
        *   Implements core business logic (e.g., user management, progress tracking).
        *   Orchestrates interactions between different services, including the `GeminiService` and the database.

3.  **`GeminiService` (AI Module)**:
    *   **Role:** A specialized Python class that encapsulates all interactions with Google's Gemini generative AI models.
    *   **Responsibilities:**
        *   Constructs prompts tailored to specific tasks (e.g., generating questions, evaluating answers, creating study plans, analyzing images).
        *   Communicates with the appropriate Gemini text or vision models.
        *   Parses responses from the AI, often expecting JSON-formatted data.
        *   Provides AI-driven functionalities like question generation, answer evaluation, chat, and content creation.

4.  **Relational Database (SQLAlchemy with SQLite/PostgreSQL)**:
    *   **Role:** Provides persistent storage for structured application data.
    *   **Responsibilities:** Stores information such as:
        *   User profiles (e.g., `User` model).
        *   Question attempts and performance data (e.g., `QuestionAttempt` model).
        *   Potentially, pre-generated questions or other application-specific data.
    *   SQLAlchemy is used as the ORM to interact with the database (likely SQLite for development and potentially PostgreSQL for production).

5.  **Vector Database (Implicit, via Retriever)**:
    *   **Role:** Enables Retrieval Augmented Generation (RAG) for contextually relevant AI responses.
    *   **Responsibilities:**
        *   Stores vector embeddings of textual content (e.g., educational materials, documents).
        *   Allows the `GeminiService` (through a `retriever` component) to perform similarity searches and fetch relevant context. This context is then used to augment prompts sent to the Gemini models, leading to more accurate and informed question generation or answer evaluation. While not explicitly detailed, this is a common pattern for such applications.

### Component Interaction Flow (Example: User Requests a Question)

1.  **Frontend:** The user interacts with the React UI to request a new question on a specific topic.
2.  **HTTP Request:** The frontend sends an HTTP request (e.g., `POST /generate_question`) to the Flask backend, including necessary data like the user's profile ID and the desired topic.
3.  **Backend Processing:**
    *   The Flask backend receives the request.
    *   It calls the `GeminiService`'s `generate_sat_question` (or a similar) method, passing user profile information and the topic.
4.  **`GeminiService` Action:**
    *   The `GeminiService` constructs a prompt.
    *   If the question generation requires specific context (RAG), the service might first use its `retriever` component to fetch relevant documents from the **Vector Database**.
    *   The service sends the prompt (potentially augmented with retrieved context) to the Google Gemini AI model.
    *   It receives the response (e.g., a JSON string containing the question, options, and explanation) and parses it.
5.  **Backend Response:** The `GeminiService` returns the generated question data to the Flask route handler. The backend then formats this into an HTTP response and sends it back to the frontend.
6.  **Frontend Update:** The React application receives the response, updates its state, and renders the new question on the user's screen.

This layered architecture allows for modularity and scalability, separating concerns between user interaction, business logic, AI processing, and data storage.
