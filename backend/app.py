# sat_gemini_agent/backend/app.py
import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from services.gemini_service import GeminiService
from flask_cors import CORS
from models import db, QuestionAttempt, User # MODIFIED: Import User model
import pandas as pd
from src.retriever import get_retriever

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")

gemini_service = GeminiService(GOOGLE_API_KEY, text_model_name='models/gemini-2.5-flash-preview-05-20', vision_model_name='models/gemini-2.5-pro-preview-05-06')

retriever = get_retriever()

# NEW ENDPOINT: Register/Get User Profile
@app.route('/user', methods=['POST', 'GET'])
def manage_user_profile():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        if not username:
            return jsonify({"error": "Username is required"}), 400

        user = User.query.filter_by(username=username).first()
        if user:
            # Update existing user profile
            user.learning_goals = json.dumps(data.get('learning_goals', []))
            user.learning_style_preference = data.get('learning_style_preference')
            user.current_knowledge_level = json.dumps(data.get('current_knowledge_level', {}))
            user.preferences = json.dumps(data.get('preferences', {}))
            db.session.commit()
            return jsonify({"message": "User profile updated successfully!", "user": user.to_dict()}), 200
        else:
            # Create new user
            new_user = User(
                username=username,
                learning_goals=json.dumps(data.get('learning_goals', [])),
                learning_style_preference=data.get('learning_style_preference'),
                current_knowledge_level=json.dumps(data.get('current_knowledge_level', {})),
                preferences=json.dumps(data.get('preferences', {}))
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "User created successfully!", "user": new_user.to_dict()}), 201
    elif request.method == 'GET':
        username = request.args.get('username')
        user_id = request.args.get('user_id')

        if username:
            user = User.query.filter_by(username=username).first()
        elif user_id:
            user = User.query.get(user_id)
        else:
            return jsonify({"error": "Username or user_id is required"}), 400

        if user:
            return jsonify({"user": user.to_dict()}), 200
        else:
            return jsonify({"error": "User not found"}), 404


# NEW ENDPOINT: Assess Knowledge
@app.route('/assess_knowledge', methods=['POST'])
def assess_knowledge_endpoint():
    data = request.json
    user_id = data.get('user_id')
    user_input = data.get('user_input')
    topic_area = data.get('topic_area')

    if not user_id or not user_input:
        return jsonify({"error": "user_id and user_input are required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        assessment_result = gemini_service.assess_knowledge(user_id, user_input, topic_area)
        if "error" in assessment_result:
            return jsonify(assessment_result), 500

        # Update the user's knowledge level in the database
        user.current_knowledge_level = json.dumps(assessment_result)
        db.session.commit()

        return jsonify({"message": "Knowledge assessed and profile updated.", "assessment": assessment_result}), 200
    except Exception as e:
        app.logger.error(f"Error in /assess_knowledge: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/save_attempt', methods=['POST'])
def save_attempt_endpoint():
    data = request.json
    try:
        # It's now important that 'user_id' is passed in the request
        user_id = data.get('userId') # Corrected from 'user_id' as frontend sends 'userId'
        if not user_id:
            return jsonify({"error": "User ID is required to save attempt."}), 400

        new_attempt = QuestionAttempt(
            user_id=user_id, # Use the provided user_id
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

@app.route('/get_performance_summary', methods=['GET'])
def get_performance_summary_endpoint():
    # MODIFIED: Allow filtering by user_id
    user_id = request.args.get('user_id')
    query = QuestionAttempt.query
    if user_id:
        query = query.filter_by(user_id=user_id)

    attempts = query.all()

    if not attempts:
        return jsonify({"message": "No practice attempts recorded yet.", "performance_data": {}}), 200

    df = pd.DataFrame([a.to_dict() for a in attempts])

    performance_by_topic = {}
    for topic in df['topic'].unique():
        topic_df = df[df['topic'] == topic]
        correct_count = topic_df['is_correct'].sum()
        incorrect_count = len(topic_df) - correct_count
        performance_by_topic[topic] = {
            'correct': int(correct_count),
            'incorrect': int(incorrect_count)
        }

    aggregated_data = {
        'math': {},
        'reading': {},
        'writing': {}
    }

    for topic, counts in performance_by_topic.items():
        if 'algebra' in topic.lower() or 'geometry' in topic.lower() or 'math' in topic.lower():
            aggregated_data['math'][topic] = counts
        elif 'reading' in topic.lower() or 'passage' in topic.lower():
            aggregated_data['reading'][topic] = counts
        elif 'writing' in topic.lower() or 'grammar' in topic.lower():
            aggregated_data['writing'][topic] = counts
        else: # For any other topics not categorized
            if 'other_topics' not in aggregated_data:
                aggregated_data['other_topics'] = {}
            aggregated_data['other_topics'][topic] = counts


    return jsonify({"message": "Performance summary retrieved.", "performance_data": aggregated_data}), 200


@app.route('/generate_question', methods=['POST'])
def generate_question_endpoint():
    data = request.json
    topic = data.get('topic')
    difficulty = data.get('difficulty', 'medium')
    question_type = data.get('question_type', 'multiple_choice')
    user_id = data.get('user_id') # NEW: Get user_id

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    user_knowledge_level = {}
    if user_id:
        user = User.query.get(user_id)
        if user and user.current_knowledge_level:
            user_knowledge_level = json.loads(user.current_knowledge_level)

    # NEW: Potentially adjust topic/difficulty based on user_knowledge_level
    # This is a simple example; more sophisticated logic would go here
    adjusted_difficulty = difficulty
    adjusted_topic = topic
    if user_knowledge_level:
        # Example: if user is 'beginner' in a topic, maybe force 'easy' difficulty
        # Or if 'needs practice', select a sub-topic they are weak in.
        # This will require more advanced logic for dynamic adjustment.
        # For now, we just pass the knowledge level to the Gemini service (if applicable)
        print(f"User {user_id} knowledge level: {user_knowledge_level}")

    try:
        # You could modify generate_sat_question to accept user_knowledge_level
        # for more dynamic question generation, but for now, we'll keep it simple.
        question_text = gemini_service.generate_sat_question(adjusted_topic, adjusted_difficulty, question_type)
        return jsonify({"question": question_text})
    except Exception as e:
        app.logger.error(f"Error generating question: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_question_from_db', methods=['POST'])
def generate_question_from_db_endpoint():
    data = request.json
    query_topic = data.get('query_topic')
    difficulty = data.get('difficulty', 'medium')
    question_type = data.get('question_type', 'multiple_choice')
    user_id = data.get('user_id') # NEW: Get user_id

    if not query_topic:
        return jsonify({"error": "Query topic is required to retrieve relevant content from the database."}), 400

    user_knowledge_level = {}
    if user_id:
        user = User.query.get(user_id)
        if user and user.current_knowledge_level:
            user_knowledge_level = json.loads(user.current_knowledge_level)
            print(f"User {user_id} knowledge level for DB question: {user_knowledge_level}")


    try:
        retrieved_docs_langchain = retriever.invoke(query_topic)
        
        context_texts = [doc.page_content for doc in retrieved_docs_langchain]
        context_combined = "\n\n".join(context_texts)

        if not context_combined.strip():
            return jsonify({"question": "Could not find relevant content in the database to generate a question for this topic. Please try a different query."})

        question_text = gemini_service.generate_sat_question_from_context(
            context_combined,
            query_topic,
            difficulty,
            question_type
            # Potentially pass user_knowledge_level here for more nuanced question generation
        )
        return jsonify({"question": question_text})
    except Exception as e:
        app.logger.error(f"Error generating question from DB: {e}")
        return jsonify({"error": f"Failed to generate question from database: {str(e)}"}), 500


@app.route('/evaluate_answer', methods=['POST'])
def evaluate_answer_endpoint():
    data = request.json
    question_text = data.get('question_text')
    user_answer = data.get('user_answer')
    correct_answer_info = data.get('correct_answer_info')
    user_id = data.get('user_id') # NEW: Get user_id (important for saving attempt)

    if not all([question_text, user_answer, correct_answer_info]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        feedback = gemini_service.evaluate_and_explain(question_text, user_answer, correct_answer_info)

        # Automatically save the attempt with the user_id
        if user_id:
            try:
                new_attempt = QuestionAttempt(
                    user_id=user_id,
                    question_text=question_text,
                    topic=data.get('topic'), # Ensure topic is passed for saving
                    difficulty=data.get('difficulty'), # Ensure difficulty is passed for saving
                    user_answer=user_answer,
                    correct_answer=correct_answer_info['answer'],
                    is_correct=feedback.get('is_correct', False),
                    time_taken_seconds=data.get('timeTakenSeconds')
                )
                db.session.add(new_attempt)
                db.session.commit()
                print(f"Attempt for user {user_id} saved after evaluation.")
            except Exception as e:
                app.logger.error(f"Error saving attempt after evaluation: {e}")
                # Don't fail the feedback response if saving attempt fails
        else:
            print("No user_id provided for attempt, skipping saving.")


        return jsonify({"feedback": feedback})
    except Exception as e:
        app.logger.error(f"Error evaluating answer: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/study_plan', methods=['POST'])
def study_plan_endpoint():
    data = request.json
    user_performance_data = data.get('user_performance_data')
    user_id = data.get('user_id') # NEW: Get user_id

    if not user_performance_data:
        return jsonify({"error": "User performance data is required"}), 400

    user_profile = {}
    if user_id:
        user = User.query.get(user_id)
        if user:
            user_profile = user.to_dict()
            print(f"Generating study plan for user {user_id} with profile: {user_profile}")
    
    try:
        # MODIFIED: Pass user_profile to generate_study_plan
        # You'll enhance generate_study_plan in gemini_service to use this.
        plan = gemini_service.generate_study_plan(user_performance_data, user_profile)
        return jsonify({"study_plan": plan})
    except Exception as e:
        app.logger.error(f"Error generating study plan: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/upload_image_question', methods=['POST'])
def upload_image_question_endpoint():
    data = request.json
    image_data_urls = data.get('imageDataUrls')
    user_prompt_text = data.get('userPromptText')
    user_id = data.get('user_id') # NEW: Get user_id

    if not image_data_urls or not isinstance(image_data_urls, list) or not user_prompt_text:
        return jsonify({"error": "An array of image data URLs and user prompt text are required"}), 400

    all_ai_responses = []
    for image_data_url in image_data_urls:
        try:
            ai_response_json = gemini_service.analyze_image_question(image_data_url, user_prompt_text)

            if "error" in ai_response_json:
                app.logger.error(f"Error analyzing one image: {ai_response_json.get('error')} - {ai_response_json.get('details')}")
                all_ai_responses.append({"error": "Failed to analyze this image", "details": ai_response_json.get("details", "")})
                continue

            ai_solution_to_save = ai_response_json.get('ai_solution', [])
            if isinstance(ai_solution_to_save, list):
                ai_solution_to_save = json.dumps(ai_solution_to_save)
            else:
                ai_solution_to_save = str(ai_solution_to_save)

            # Save image question attempt
            if user_id:
                new_attempt = QuestionAttempt(
                    user_id=user_id, # Use the provided user_id
                    is_image_question=True,
                    image_base64_preview=image_data_url[:200] + "..." if len(image_data_url) > 200 else image_data_url,
                    user_image_prompt=user_prompt_text,
                    ai_generated_answer=ai_response_json.get('ai_answer', ''),
                    ai_generated_solution=ai_solution_to_save
                )
                db.session.add(new_attempt)
                db.session.commit()
                print(f"Image question attempt for user {user_id} saved.")
            else:
                print("No user_id provided for image question attempt, skipping saving.")


            all_ai_responses.append(ai_response_json)

        except Exception as e:
            app.logger.error(f"Error processing image in loop: {e}")
            all_ai_responses.append({"error": "An unexpected error occurred for this image", "details": str(e)})

    if not all_ai_responses:
        return jsonify({"error": "No images were successfully analyzed."}), 500

    # Ensure to return a 200 OK or 207 Multi-Status if some failed but others succeeded.
    # For simplicity, if at least one succeeded, return 200.
    return jsonify({"message": "Images analyzed successfully!", "aiResponses": all_ai_responses}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)