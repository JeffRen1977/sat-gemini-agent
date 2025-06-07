## GeminiService Operations

The `GeminiService` class is a core component of the backend, responsible for interacting with Google's Gemini large language models to provide various AI-driven functionalities. It orchestrates prompt engineering, model interaction, and response parsing.

### Model Usage

`GeminiService` utilizes different Gemini models for specific tasks:

-   **Text Generation & Reasoning:** For most text-based tasks such as question generation, evaluation, study plan creation, and chat, it primarily uses a text model like **`gemini-pro`** or a similar variant available at the time of implementation (e.g., potentially `'gemini-1.5-flash-latest'` or a specific preview version if that was current).
-   **Vision Capabilities:** For analyzing image-based questions, it employs a multimodal vision model, likely **`gemini-pro-vision`** or a newer equivalent capable of processing both text and image inputs (e.g., potentially `'models/gemini-1.5-pro-latest'` if it supports vision and was available).

### Key Methods and Operations

The service exposes several methods to interact with the Gemini models:

1.  **`generate_sat_question(self, user_profile, subject, difficulty)`**
    *   **Purpose:** Generates a new SAT-style question based on the user's profile, a specified subject, and difficulty level.
    *   **Inputs/Prompts:** Constructs a detailed prompt incorporating the `user_profile` (which may include knowledge levels, learning style, past performance), the desired `subject` (e.g., Math, Reading, Writing), and `difficulty` (e.g., Easy, Medium, Hard). The prompt instructs the AI to create a question, provide options (if multiple-choice), specify the correct answer, and give an explanation.
    *   **Output:** Expects a JSON formatted string from the AI, which is then parsed.

2.  **`evaluate_and_explain(self, user_profile, question, user_answer, context=None)`**
    *   **Purpose:** Evaluates a user's answer to a given question and provides an explanation for why the answer is correct or incorrect.
    *   **Inputs/Prompts:** Takes the `user_profile`, the `question` text, the `user_answer`, and optional `context` (retrieved from a vector DB or other sources). The prompt asks the AI to assess the correctness of the `user_answer` against the `question` (and its known correct answer/logic, often included in the prompt or implied if the question was AI-generated previously) and to generate a helpful explanation.
    *   **Output:** Expects a JSON response containing the evaluation (e.g., "correct", "incorrect", "partially correct") and the explanation.

3.  **`generate_study_plan(self, user_profile, goals, time_frame)`**
    *   **Purpose:** Creates a personalized study plan for a user based on their profile, learning goals, and available time frame.
    *   **Inputs/Prompts:** Uses the `user_profile` (knowledge gaps, strengths), stated `goals` (e.g., "improve SAT Math score by 100 points"), and `time_frame` (e.g., "3 months"). The prompt guides the AI to suggest topics, resources, and a schedule.
    *   **Output:** Expects a JSON formatted study plan, likely with sections for weekly/daily tasks, topics to cover, and recommended resources.

4.  **`analyze_image_question(self, user_profile, image_data, question_text=None)`**
    *   **Purpose:** Analyzes an image provided by the user and generates a question based on it, or answers a user's question about the image.
    *   **Inputs/Prompts:** Takes `user_profile`, `image_data` (the raw image bytes/format), and an optional `question_text` from the user if they are asking something specific about the image. The prompt, along with the image, is sent to the vision model to either formulate a relevant question (e.g., "What is the main subject of this image?") or answer the user's query.
    *   **Output:** Expects a JSON response containing the AI-generated question about the image or the answer to the user's question.

5.  **`assess_knowledge(self, user_profile, topics)`**
    *   **Purpose:** Assesses the user's knowledge level on a given set of topics, possibly by generating a few targeted questions or by having the user self-report and then refining based on interaction.
    *   **Inputs/Prompts:** Takes the `user_profile` and a list of `topics`. The prompt might ask the AI to generate a series of questions or scenarios to gauge understanding, or to process self-reported proficiencies and suggest areas for validation.
    *   **Output:** Expects a JSON response summarizing the assessed knowledge levels for the specified topics.

6.  **`generate_sat_question_from_context(self, user_profile, context, subject, difficulty)`**
    *   **Purpose:** Generates an SAT-style question specifically based on a provided piece of context (e.g., a text passage).
    *   **Inputs/Prompts:** Similar to `generate_sat_question` but with the addition of a `context` string. The prompt instructs the AI to create a question that can be answered using the given `context`, tailored to the `user_profile`, `subject`, and `difficulty`.
    *   **Output:** Expects a JSON formatted question, options, answer, and explanation.

7.  **Chat Methods:**
    *   **`start_chat_session(self, user_profile)`**
        *   **Purpose:** Initializes a new chat session with the AI, potentially setting a context or persona for the AI based on the `user_profile`.
        *   **Inputs/Prompts:** Uses `user_profile` to tailor the initial chat prompt (e.g., "You are a friendly SAT tutor. The user is focusing on Math.").
        *   **Output:** Returns a session identifier and the initial AI message.
    *   **`send_chat_message(self, chat_session_id, user_message, history)`**
        *   **Purpose:** Sends a user's message to the AI within an ongoing chat session and gets a response.
        *   **Inputs/Prompts:** Takes the `chat_session_id`, the `user_message`, and the `history` of the conversation so far. The prompt includes the history and the new message to allow the AI to respond contextually.
        *   **Output:** Returns the AI's response.

8.  **`simulate_interview(self, user_profile, job_description, topics)`**
    *   **Purpose:** Simulates a job interview experience for the user.
    *   **Inputs/Prompts:** Uses `user_profile`, a `job_description`, and specific `topics` to cover. The prompt sets up the AI to act as an interviewer, asking relevant questions based on the job role and topics.
    *   **Output:** The AI's questions or responses in the simulated interview, likely expecting JSON for structured interaction if the simulation involves turn-by-turn evaluation or feedback.

### JSON Response Handling

A common pattern across many `GeminiService` methods is the expectation that the Gemini API will return a response formatted as a JSON string. The service then attempts to parse this JSON string into a Python dictionary or list using `json.loads()`.

### Personalization

User profile data is frequently incorporated into the prompts sent to the Gemini models. This allows for personalization of:
-   Question difficulty and topic selection.
-   The tone and style of explanations and chat interactions.
-   The focus areas in generated study plans.

### Error Handling

The service includes basic error handling for JSON parsing. If the AI's response is not valid JSON, a `ValueError` (or a custom exception wrapping it) is typically caught, and an error message or a fallback response is generated. This prevents the application from crashing due to malformed AI output.

This structured approach allows `GeminiService` to be a versatile interface to Google's powerful AI models, adapting them to the specific needs of the educational application.
