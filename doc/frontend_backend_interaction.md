## Frontend-Backend Interaction

This section provides a high-level overview of how the frontend and backend components of the application are expected to interact.

### Frontend (React Application)

The frontend of the application is presumed to be a React single-page application (SPA) located in the `frontend/` directory. Its primary responsibilities include:

-   **User Interface (UI) Rendering:** Displaying the web pages, forms, questions, study plans, and other visual elements to the user.
-   **User Input Management:** Capturing user actions, such as text input, button clicks, file uploads (for image questions), and selections.
-   **State Management:** Keeping track of the application's state on the client-side (e.g., current user, ongoing quiz, chat history).

### Communication Protocol

The React frontend communicates with the Flask backend via **HTTP requests**. The backend exposes a series of API endpoints (as detailed in `backend_api_endpoints.md`), and the frontend consumes these endpoints to send and receive data.

### API Requests

To interact with the backend, the frontend JavaScript code will use:

-   The built-in **`fetch` API** or
-   HTTP client libraries like **`axios`**.

These tools allow the frontend to make asynchronous requests to the backend API endpoints, such as:

-   `POST` requests to send data (e.g., submitting user profile information to `/user`, an answer to `/evaluate_answer`, or an image to `/upload_image_question`).
-   `GET` requests to retrieve data (e.g., fetching user performance from `/get_performance_summary` or a question from `/generate_question_from_db`).

### Data Flow

1.  **User Interaction:** A user interacts with the UI (e.g., clicks a button to generate a question).
2.  **Frontend Request:** The React application captures this interaction and makes an HTTP request to the appropriate backend API endpoint (e.g., `POST /generate_question`). This request might include a JSON payload in its body or parameters in the URL.
3.  **Backend Processing:** The Flask backend receives the request, processes it (potentially interacting with `GeminiService` and the database), and formulates a response.
4.  **Backend Response:** The backend sends an HTTP response back to the frontend, typically containing a JSON payload (e.g., the generated question data).
5.  **Frontend Update:** The frontend JavaScript code receives the response, parses the JSON data, updates its internal state, and re-renders the UI to display the new information to the user (e.g., showing the generated question).

This client-server architecture allows for a clear separation of concerns, with the frontend handling presentation and user interaction, and the backend managing business logic, data persistence, and AI model integration.
