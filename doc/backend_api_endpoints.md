## Backend API Endpoints

This document details the main API endpoints provided by the backend application, their HTTP methods, URL paths, and purposes.

### User Management

-   **Endpoint:** `POST /user`
    -   **Purpose:** Creates a new user profile or updates an existing one. Expects user details in the request body.
-   **Endpoint:** `GET /user`
    -   **Purpose:** Retrieves an existing user's profile. User identification would likely be handled via session cookies or a token sent in the headers.

### Knowledge Assessment & Practice

-   **Endpoint:** `POST /assess_knowledge`
    -   **Purpose:** Allows a user to submit their perceived knowledge levels for various topics. This information is likely used to personalize question generation or study plans.
-   **Endpoint:** `POST /save_attempt`
    -   **Purpose:** Saves the details of a user's attempt at a question, including the question itself, the user's answer, whether it was correct, and any feedback.
-   **Endpoint:** `GET /get_performance_summary`
    -   **Purpose:** Retrieves a summary of the user's past performance, potentially including statistics like the number of questions attempted, percentage correct, and performance by topic.

### Question Handling

-   **Endpoint:** `POST /generate_question`
    -   **Purpose:** Generates a new question for the user, likely based on their learning profile, past performance, or selected topics. May involve interaction with the `GeminiService`.
-   **Endpoint:** `GET /generate_question_from_db`
    -   **Purpose:** Retrieves a question from the existing database of questions, possibly filtered by topic or difficulty.
-   **Endpoint:** `POST /evaluate_answer`
    -   **Purpose:** Evaluates a user's submitted answer to a question. This involves sending the question, user's answer, and relevant context to the `GeminiService` for assessment.
-   **Endpoint:** `POST /upload_image_question`
    -   **Purpose:** Allows users to submit questions based on an uploaded image. The backend would process the image and potentially use multimodal AI capabilities to understand and formulate a question related to the image content.

### Study Planning

-   **Endpoint:** `POST /study_plan`
    -   **Purpose:** Generates a personalized study plan for the user. This plan is likely based on their assessed knowledge, performance history, and learning goals. It may suggest topics to focus on or questions to practice.

*(Note: Specific request/response formats and authentication mechanisms are not detailed here but would be defined in the full API specification.)*
