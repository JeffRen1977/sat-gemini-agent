# backend/app.py
import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from services.gemini_service import GeminiService
from flask_cors import CORS
from models import db, QuestionAttempt # <--- IMPORT DB AND MODEL
import pandas as pd # <--- IMPORT PANDAS

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # SQLite database file in your backend folder
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # <--- INITIALIZE DB WITH APP

# --- ADD THIS TO CREATE TABLES (FOR DEVELOPMENT ONLY) ---
# In a real app, use Flask-Migrate or Alembic for proper migrations
with app.app_context():
    db.create_all()
# --- END DB CREATION ---

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")

gemini_service = GeminiService(GEMINI_API_KEY)

# TEMPORARY: Remove this line after you got the model list
# gemini_service.list_available_models() # <-- REMOVE OR COMMENT OUT THIS LINE

# =========================================================
# NEW ENDPOINT: Save Question Attempt
# =========================================================
@app.route('/save_attempt', methods=['POST'])
def save_attempt_endpoint():
    data = request.json
    try:
        new_attempt = QuestionAttempt(
            user_id=data.get('userId', 'anonymous'), # Add user_id if you implement auth
            question_text=data['questionText'],
            topic=data['topic'],
            difficulty=data['difficulty'],
            user_answer=data['userAnswer'],
            correct_answer=data['correctAnswer'],
            is_correct=data['isCorrect'],
            time_taken_seconds=data.get('timeTakenSeconds')
        )
        db.session.add(new_attempt)
        db.session.commit()
        return jsonify({"message": "Attempt saved successfully!"}), 201
    except KeyError as e:
        app.logger.error(f"Missing data for saving attempt: {e}")
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except Exception as e:
        app.logger.error(f"Error saving attempt: {e}")
        return jsonify({"error": str(e)}), 500

# =========================================================
# NEW ENDPOINT: Get Aggregated Performance Summary for Study Plan
# =========================================================
@app.route('/get_performance_summary', methods=['GET'])
def get_performance_summary_endpoint():
    # In a real app, you'd filter by user_id here
    attempts = QuestionAttempt.query.all()

    if not attempts:
        return jsonify({"message": "No practice attempts recorded yet.", "performance_data": {}}), 200

    # Convert attempts to a pandas DataFrame for easy aggregation
    df = pd.DataFrame([a.to_dict() for a in attempts])

    # Basic aggregation: correct vs incorrect count by topic
    performance_by_topic = {}
    for topic in df['topic'].unique():
        topic_df = df[df['topic'] == topic]
        correct_count = topic_df['is_correct'].sum()
        incorrect_count = len(topic_df) - correct_count
        performance_by_topic[topic] = {
            'correct': int(correct_count),
            'incorrect': int(incorrect_count)
        }

    # You can add more sophisticated aggregation here (e.g., by difficulty, average time)
    # For now, we'll mimic the old userPerformance structure for compatibility with Gemini prompt
    aggregated_data = {
        'math': {},
        'reading': {},
        'writing': {}
    }

    for topic, counts in performance_by_topic.items():
        # Simple mapping to SAT sections
        if 'algebra' in topic.lower() or 'geometry' in topic.lower() or 'math' in topic.lower():
            aggregated_data['math'][topic] = counts
        elif 'reading' in topic.lower() or 'passage' in topic.lower():
            aggregated_data['reading'][topic] = counts
        elif 'writing' in topic.lower() or 'grammar' in topic.lower():
            aggregated_data['writing'][topic] = counts
        else:
            # Fallback for topics not explicitly mapped
            aggregated_data[topic] = counts


    return jsonify({"message": "Performance summary retrieved.", "performance_data": aggregated_data}), 200


@app.route('/generate_question', methods=['POST'])
def generate_question_endpoint():
    data = request.json
    topic = data.get('topic')
    difficulty = data.get('difficulty', 'medium')
    question_type = data.get('question_type', 'multiple_choice')

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    try:
        question_text = gemini_service.generate_sat_question(topic, difficulty, question_type)
        return jsonify({"question": question_text})
    except Exception as e:
        app.logger.error(f"Error generating question: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/evaluate_answer', methods=['POST'])
def evaluate_answer_endpoint():
    data = request.json
    # The 'question' key in the payload from frontend should be the raw text
    question_text = data.get('question_text') # Renamed from 'question' to avoid confusion
    user_answer = data.get('user_answer')
    correct_answer_info = data.get('correct_answer_info') # {'answer': '...', 'explanation': '...'}

    if not all([question_text, user_answer, correct_answer_info]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Pass question_text (raw text) to gemini_service
        feedback = gemini_service.evaluate_and_explain(question_text, user_answer, correct_answer_info)
        return jsonify({"feedback": feedback}) # feedback is now a JSON object from gemini_service
    except Exception as e:
        app.logger.error(f"Error evaluating answer: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/study_plan', methods=['POST'])
def study_plan_endpoint():
    data = request.json
    # user_performance_data is now expected to come from the frontend (via get_performance_summary)
    user_performance_data = data.get('user_performance_data')

    if not user_performance_data:
        return jsonify({"error": "User performance data is required"}), 400

    try:
        plan = gemini_service.generate_study_plan(user_performance_data)
        return jsonify({"study_plan": plan})
    except Exception as e:
        app.logger.error(f"Error generating study plan: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)