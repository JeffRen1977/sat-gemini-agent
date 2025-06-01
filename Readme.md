# SAT Gemini Agent

This project is an AI-powered SAT test preparation agent using Google Gemini for natural language processing and a Flask backend with a React frontend.

## Features:
- Generates SAT-style questions (Math, Reading) with varying difficulty.
- Evaluates user answers and provides detailed, structured feedback.
- Generates personalized study plans based on user performance.
- Tracks question attempts and performance data using a SQLite database.

## Setup Instructions

### 1. Clone the Repository (if applicable, otherwise create the directories)
If you're starting from scratch, manually create the `sat-gemini-agent` directory and then `backend/` and `frontend/` inside it, and follow the structure above.

### 2. Google Gemini API Key
- Go to [Google AI Studio](https://aistudio.google.com/app/apikey) to get your Gemini API key.
- Create a file `sat-gemini-agent/backend/.env` and add your API key:


### 3. Backend Setup (Python/Flask)

1.  Navigate to the `backend` directory:
  ```bash
  cd sat-gemini-agent/backend/
  ```
2.  Create and activate a Python virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On Windows: .\venv\Scripts\activate
  ```
3.  Install the required Python packages:
  ```bash
  pip install -r requirements.txt
  ```
4.  Run the Flask application:
  ```bash
  python3 app.py
  ```
  - The backend will start on `http://127.0.0.1:5000` (or `http://localhost:5000`).
  - The first time it runs, it will create a `site.db` file in the `backend/` directory for the database.
  - Keep this terminal window open and running.

### 4. Frontend Setup (React)

1.  Navigate to the `frontend` directory in a **new terminal window**:
  ```bash
  cd sat-gemini-agent/frontend/
  ```
2.  Install Node.js and npm (if you haven't already). Using `nvm` (Node Version Manager) is recommended:
  - Install `nvm`: `brew install nvm` (on macOS) or follow instructions on [nvm-sh.com](https://nvm.sh/).
  - Configure `nvm` in your shell profile (`~/.zshrc` or `~/.bash_profile`) as per `brew install nvm` output.
  - Open a new terminal or `source ~/.zshrc` (or `~/.bash_profile`).
  - Install a compatible Node.js LTS version (e.g., Node.js 18): `nvm install 18` and `nvm use 18`.
3.  Install the frontend dependencies:
  ```bash
  npm install
  ```
4.  Create a file `sat-gemini-agent/frontend/.env` and set your backend API URL:
  ```
  REACT_APP_API_URL=http://localhost:5000
  ```
  (Adjust port if you changed it in `backend/app.py`)
5.  Start the React development server:
  ```bash
  # Use this to resolve OpenSSL errors with newer Node.js versions
  NODE_OPTIONS=--openssl-legacy-provider npm start
  ```
  - The frontend will open in your browser at `http://localhost:3000`.
  - Keep this terminal window open and running.

## Usage

1.  Ensure both the backend (Flask) and frontend (React) servers are running in separate terminal windows.
2.  Open your browser to `http://localhost:3000`.
3.  Click "Generate Math Question" or "Generate Reading Question" to get a practice problem.
4.  Type your answer and click "Submit Answer" to get AI feedback.
5.  After answering some questions, click "Get Personalized Study Plan" to see a summary based on your performance.
