# sat_gemini_agent/backend/app.py
import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from services.gemini_service import GeminiService
from flask_cors import CORS
from models import db, QuestionAttempt, User, MockTest, MockTestSection, UserMockTestAttempt, Word, WordList, UserWordProgress, EssayTopic, UserEssaySubmission, word_to_word_list
import pandas as pd
from src.retriever import get_retriever
from datetime import datetime

load_dotenv()

app = Flask(__name__)
# Initialize CORS *before* any routes are defined or blueprints are registered
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    # Seed initial data for MockTest
    if not MockTest.query.first():
        sample_mock_test = MockTest(
            title="Full SAT Practice Test 1",
            description="A comprehensive practice test covering all SAT sections.",
            total_duration_minutes=180  # Example: 3 hours
        )
        db.session.add(sample_mock_test)
        db.session.commit()

        section1 = MockTestSection(
            mock_test_id=sample_mock_test.id,
            title="Reading Comprehension",
            order=1,
            duration_minutes=65,
            question_generation_config=json.dumps({"topic": "SAT Reading", "difficulty": "medium", "count": 5, "type": "multiple_choice"})
        )
        section2 = MockTestSection(
            mock_test_id=sample_mock_test.id,
            title="Writing and Language",
            order=2,
            duration_minutes=35,
            question_generation_config=json.dumps({"topic": "SAT Writing - Grammar", "difficulty": "medium", "count": 4, "type": "multiple_choice"})
        )
        section3 = MockTestSection(
            mock_test_id=sample_mock_test.id,
            title="Math - No Calculator",
            order=3,
            duration_minutes=25,
            question_generation_config=json.dumps({"topic": "SAT Math - Algebra", "difficulty": "hard", "count": 3, "type": "multiple_choice"})
        )
        section4 = MockTestSection(
            mock_test_id=sample_mock_test.id,
            title="Math - Calculator",
            order=4,
            duration_minutes=55,
            question_generation_config=json.dumps({"topic": "SAT Math - Data Analysis", "difficulty": "medium", "count": 5, "type": "multiple_choice"})
        )
        db.session.add_all([section1, section2, section3, section4])
        db.session.commit()
        app.logger.info("Sample mock test and sections created.")

    # Seed initial data for Vocabulary Builder
    if not WordList.query.first():
        common_list = WordList(name="SAT Common Words Pack 1", description="A list of frequently encountered SAT vocabulary words.")
        advanced_list = WordList(name="Advanced SAT Vocabulary", description="Challenging words for students aiming for higher scores.")
        db.session.add_all([common_list, advanced_list])
        db.session.commit()

        words_data = [
            {"term": "Ephemeral", "definition": "Lasting for a very short time.", "example_sentence": "The beauty of the sunset is ephemeral.", "difficulty_level": "medium", "lists": [common_list]},
            {"term": "Ubiquitous", "definition": "Present, appearing, or found everywhere.", "example_sentence": "Mobile phones have become ubiquitous in modern society.", "difficulty_level": "medium", "lists": [common_list, advanced_list]},
            {"term": "Serendipity", "definition": "The occurrence and development of events by chance in a happy or beneficial way.", "example_sentence": "Discovering the old bookstore was pure serendipity.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Alacrity", "definition": "Brislisk and cheerful readiness.", "example_sentence": "She accepted the invitation with alacrity.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Mellifluous", "definition": "Pleasant and musical to hear.", "example_sentence": "Her mellifluous voice captivated the audience.", "difficulty_level": "medium", "lists": [common_list]},
            {"term": "Capricious", "definition": "Given to sudden and unaccountable changes of mood or behavior.", "example_sentence": "The weather was capricious, changing from sunny to stormy in minutes.", "difficulty_level": "medium", "lists": [common_list, advanced_list]},
            {"term": "Gregarious", "definition": "Fond of company; sociable.", "example_sentence": "He was a gregarious and outgoing person, always surrounded by friends.", "difficulty_level": "medium", "lists": [common_list]},
            {"term": "Laconic", "definition": "Using very few words.", "example_sentence": "His laconic reply suggested he wasn't interested.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Pernicious", "definition": "Having a harmful effect, especially in a gradual or subtle way.", "example_sentence": "The pernicious influence of misinformation can be devastating.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Quixotic", "definition": "Extremely idealistic; unrealistic and impractical.", "example_sentence": "His quixotic quest to end world hunger was admirable but ultimately futile.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Conundrum", "definition": "A confusing and difficult problem or question.", "example_sentence": "The issue of balancing economic growth with environmental protection is a global conundrum.", "difficulty_level": "medium", "lists": [common_list]},
            {"term": "Equivocate", "definition": "Use ambiguous language so as to conceal the truth or avoid committing oneself.", "example_sentence": "When asked about the missing funds, the treasurer began to equivocate, raising suspicions.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Fortuitous", "definition": "Happening by chance rather than intention.", "example_sentence": "It was a fortuitous coincidence that they met at the airport after years apart.", "difficulty_level": "medium", "lists": [common_list]},
            {"term": "Hedonist", "definition": "A person who believes that the pursuit of pleasure is the most important thing in life; a pleasure-seeker.", "example_sentence": "The celebrity lived the life of a hedonist, indulging in every luxury imaginable.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Impecunious", "definition": "Having little or no money; penniless.", "example_sentence": "Despite his brilliant ideas, the impecunious inventor struggled to find funding for his projects.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Jubilant", "definition": "Feeling or expressing great happiness and triumph.", "example_sentence": "The crowd was jubilant after their team won the championship in overtime.", "difficulty_level": "medium", "lists": [common_list]},
            {"term": "Knell", "definition": "The sound of a bell, especially when rung solemnly for a death or funeral.", "example_sentence": "The church bells tolled a mournful knell as the procession passed.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Luminous", "definition": "Emitting or reflecting light; shining.", "example_sentence": "The moon cast a luminous glow over the calm lake.", "difficulty_level": "medium", "lists": [common_list]},
            {"term": "Malediction", "definition": "A magical word or phrase uttered with the intention of bringing about evil or destruction; a curse.", "example_sentence": "The witch muttered a malediction under her breath as the hero escaped.", "difficulty_level": "hard", "lists": [advanced_list]},
            {"term": "Nonchalant", "definition": "Feeling or appearing casually calm and relaxed; not displaying anxiety, interest, or enthusiasm.", "example_sentence": "He gave a nonchalant shrug when asked about the strict new rules.", "difficulty_level": "medium", "lists": [common_list]},
        ]

        for data in words_data:
            word = Word.query.filter_by(term=data["term"]).first()
            if not word:
                word = Word(
                    term=data["term"],
                    definition=data["definition"],
                    example_sentence=data["example_sentence"],
                    difficulty_level=data["difficulty_level"]
                )
                db.session.add(word)
                db.session.commit()

            for wl_obj in data["lists"]:
                if word not in wl_obj.words:
                    wl_obj.words.append(word)
        db.session.commit()
        app.logger.info("Sample word lists and words created.")

    # Seed initial data for Essay Topics
    if not EssayTopic.query.first():
        essay_topics_data = [
            {
                "title": "The Role of Technology in Education",
                "description": "Write an essay analyzing the impact of technology on modern education. Consider both the benefits and drawbacks, and support your arguments with specific examples.",
                "category": "Argumentative"
            },
            {
                "title": "Analysis of a Pivotal Moment in History",
                "description": "Choose a significant historical event and write an essay analyzing its causes, consequences, and overall importance. Use evidence from historical sources to support your analysis.",
                "category": "Analytical"
            },
            {
                "title": "The Value of Standardized Testing",
                "description": "Write an essay that argues for or against the use of standardized testing as a primary measure for college admissions. Support your position with clear reasoning and examples.",
                "category": "Argumentative"
            }
        ]
        for topic_data in essay_topics_data:
            topic = EssayTopic(**topic_data)
            db.session.add(topic)
        db.session.commit()
        app.logger.info("Sample essay topics created.")


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
        user_id = data.get('userId')
        if not user_id:
            return jsonify({"error": "User ID is required to save attempt."}), 400

        new_attempt = QuestionAttempt(
            user_id=user_id,
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
        else:
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
    user_id = data.get('user_id')

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    user_knowledge_level = {}
    if user_id:
        user = User.query.get(user_id)
        if user and user.current_knowledge_level:
            user_knowledge_level = json.loads(user.current_knowledge_level)

    adjusted_difficulty = difficulty
    adjusted_topic = topic
    if user_knowledge_level:
        print(f"User {user_id} knowledge level: {user_knowledge_level}")

    try:
        question_data = gemini_service.generate_sat_question(adjusted_topic, adjusted_difficulty, question_type)
        
        if "error" in question_data:
            return jsonify({"error": question_data.get("error"), "details": question_data.get("details", "")}), 500

        return jsonify({"question": question_data})
    except Exception as e:
        app.logger.error(f"Error generating question: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_question_from_db', methods=['POST'])
def generate_question_from_db_endpoint():
    data = request.json
    query_topic = data.get('query_topic')
    difficulty = data.get('difficulty', 'medium')
    question_type = data.get('question_type', 'multiple_choice')
    user_id = data.get('user_id')

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

        question_data = gemini_service.generate_sat_question_from_context(
            context_combined,
            query_topic,
            difficulty,
            question_type
        )

        if "error" in question_data:
            return jsonify({"error": question_data.get("error"), "details": question_data.get("details", "")}), 500

        return jsonify({"question": question_data})
    except Exception as e:
        app.logger.error(f"Error generating question from DB: {e}")
        return jsonify({"error": f"Failed to generate question from database: {str(e)}"}), 500


@app.route('/evaluate_answer', methods=['POST'])
def evaluate_answer_endpoint():
    data = request.json
    question_text = data.get('question_text')
    user_answer = data.get('user_answer')
    correct_answer_info = data.get('correct_answer_info')
    user_id = data.get('user_id')

    if not all([question_text, user_answer, correct_answer_info]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        feedback = gemini_service.evaluate_and_explain(
            question=question_text,
            user_answer=user_answer,
            correct_answer_info=correct_answer_info
        )

        if user_id:
            try:
                new_attempt = QuestionAttempt(
                    user_id=user_id,
                    question_text=question_text,
                    topic=data.get('topic'),
                    difficulty=data.get('difficulty'),
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
    user_id = data.get('user_id')

    if not user_performance_data:
        return jsonify({"error": "User performance data is required"}), 400

    user_profile = {}
    if user_id:
        user = User.query.get(user_id)
        if user:
            user_profile = user.to_dict()
            print(f"Generating study plan for user {user_id} with profile: {user_profile}")
    
    try:
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
    user_id = data.get('user_id')

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

            if user_id:
                new_attempt = QuestionAttempt(
                    user_id=user_id,
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

    return jsonify({"message": "Images analyzed successfully!", "aiResponses": all_ai_responses}), 200

# Mock Test Endpoints
@app.route('/mock_tests', methods=['GET'])
def get_mock_tests():
    try:
        tests = MockTest.query.all()
        return jsonify([test.to_dict() for test in tests]), 200
    except Exception as e:
        app.logger.error(f"Error fetching mock tests: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mock_tests/<int:test_id>/start', methods=['POST'])
def start_mock_test_attempt(test_id):
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    mock_test = MockTest.query.get(test_id)
    if not mock_test:
        return jsonify({"error": "Mock test not found"}), 404

    try:
        existing_attempt = UserMockTestAttempt.query.filter_by(
            user_id=user_id,
            mock_test_id=test_id,
            status='started'
        ).first()

        if existing_attempt:
             return jsonify({"error": "An active attempt for this test already exists. Please complete or abandon it first."}), 409

        new_attempt = UserMockTestAttempt(
            user_id=user_id,
            mock_test_id=test_id,
            start_time=datetime.utcnow(),
            status='started',
            score_details=json.dumps({})
        )
        db.session.add(new_attempt)
        db.session.commit()

        first_section = MockTestSection.query.filter_by(mock_test_id=test_id, order=1).first()
        if not first_section:
            return jsonify({"error": "Test has no sections defined"}), 500

        return jsonify({
            "message": "Mock test attempt started successfully.",
            "attempt_id": new_attempt.id,
            "first_section": first_section.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error starting mock test attempt: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/mock_tests/attempt/<int:attempt_id>/section/<int:section_order>', methods=['GET'])
def get_mock_test_section(attempt_id, section_order):
    try:
        attempt = UserMockTestAttempt.query.get(attempt_id)
        if not attempt:
            return jsonify({"error": "Mock test attempt not found"}), 404

        if attempt.status == 'started':
            attempt.status = 'in_progress'
            db.session.commit()

        section = MockTestSection.query.filter_by(
            mock_test_id=attempt.mock_test_id,
            order=section_order
        ).first()

        if not section:
            return jsonify({"error": f"Section with order {section_order} not found for this mock test"}), 404

        config = json.loads(section.question_generation_config)
        questions = []

        for _ in range(config.get('count', 0)):
            question_data = gemini_service.generate_sat_question(
                topic=config['topic'],
                difficulty=config['difficulty'],
                question_type=config.get('type', 'multiple_choice')
            )
            
            if "error" in question_data:
                app.logger.error(f"Error generating or parsing a question from Gemini: {question_data.get('details')}")
                questions.append({"error": "Failed to generate or parse a question.", "details": question_data.get('details', '')})
            else:
                question_data['temp_id'] = os.urandom(4).hex()
                questions.append(question_data)


        return jsonify({
            "section_details": section.to_dict(),
            "questions": questions
        }), 200

    except Exception as e:
        app.logger.error(f"Error retrieving mock test section: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mock_tests/attempt/<int:attempt_id>/section/<int:section_order>/submit', methods=['POST'])
def submit_mock_test_section(attempt_id, section_order):
    data = request.json
    user_id = data.get('user_id')
    answers = data.get('answers')

    if not user_id or not answers:
        return jsonify({"error": "user_id and answers are required"}), 400

    attempt = UserMockTestAttempt.query.get(attempt_id)
    if not attempt:
        return jsonify({"error": "Mock test attempt not found"}), 404
    if attempt.user_id != user_id:
        return jsonify({"error": "User does not match attempt owner"}), 403
    if attempt.status == 'completed':
        return jsonify({"error": "This test attempt has already been completed."}), 400


    current_section = MockTestSection.query.filter_by(
        mock_test_id=attempt.mock_test_id,
        order=section_order
    ).first()
    if not current_section:
        return jsonify({"error": f"Section {section_order} not found for this test."}), 404

    section_score = 0
    num_correct = 0
    detailed_feedback = []

    for answer_submission in answers:
        feedback = gemini_service.evaluate_and_explain(
            question=answer_submission['question_text'],
            user_answer=answer_submission['user_answer'],
            correct_answer_info=answer_submission['correct_answer_info']
        )

        if feedback.get('is_correct'):
            num_correct += 1

        detailed_feedback.append({
            "temp_id": answer_submission.get("temp_id"),
            "question_text": answer_submission['question_text'],
            "user_answer": answer_submission['user_answer'],
            "feedback": feedback
        })

    if answers:
        section_score = (num_correct / len(answers)) * 100

    score_details_dict = json.loads(attempt.score_details) if attempt.score_details else {}
    if "sections" not in score_details_dict:
        score_details_dict["sections"] = {}

    section_key = current_section.title.lower().replace(" ", "_").replace("-", "_")

    time_taken_for_section = data.get('time_taken_seconds_for_section', 0)

    score_details_dict["sections"][section_key] = {
        "score_percentage": round(section_score, 2),
        "correct": num_correct,
        "total": len(answers),
        "allotted_time_seconds": current_section.duration_minutes * 60,
        "time_taken_seconds": time_taken_for_section,
        "feedback_items": detailed_feedback
    }
    attempt.score_details = json.dumps(score_details_dict)

    next_section_order = None
    max_order = db.session.query(db.func.max(MockTestSection.order)).filter_by(mock_test_id=attempt.mock_test_id).scalar()
    if section_order < max_order:
        next_section_order = section_order + 1

    db.session.commit()

    return jsonify({
        "message": f"Section {section_order} submitted successfully.",
        "section_score": round(section_score, 2),
        "next_section_order": next_section_order,
        "detailed_feedback": detailed_feedback
    }), 200


@app.route('/mock_tests/attempt/<int:attempt_id>/complete', methods=['POST'])
def complete_mock_test_attempt(attempt_id):
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    attempt = UserMockTestAttempt.query.get(attempt_id)
    if not attempt:
        return jsonify({"error": "Mock test attempt not found"}), 404
    if attempt.user_id != user_id:
        return jsonify({"error": "User does not match attempt owner"}), 403
    if attempt.status == 'completed':
        return jsonify({"message": "Attempt already completed.", "final_results": json.loads(attempt.score_details) if attempt.score_details else {}}), 200


    attempt.end_time = datetime.utcnow()
    attempt.status = 'completed'

    current_score_details = json.loads(attempt.score_details) if attempt.score_details else {"sections": {}}

    total_correct_overall = 0
    total_questions_overall = 0

    total_percentage_sum = 0
    num_sections_scored = 0

    if "sections" in current_score_details:
        for section_key, section_data in current_score_details["sections"].items():
            total_correct_overall += section_data.get('correct', 0)
            total_questions_overall += section_data.get('total', 0)
            total_percentage_sum += section_data.get('score_percentage', 0)
            if section_data.get('total', 0) > 0 :
                 num_sections_scored +=1


    final_score_details_structured = {
        "overall_score_percentage": round((total_correct_overall / total_questions_overall) * 100 if total_questions_overall > 0 else 0, 2),
        "scaled_overall_score": total_percentage_sum * 8 if num_sections_scored > 0 else 0,
        "total_correct_overall": total_correct_overall,
        "total_questions_overall": total_questions_overall,
        "sections": current_score_details.get("sections", {})
    }

    attempt.score_details = json.dumps(final_score_details_structured)

    db.session.commit()

    return jsonify({
        "message": "Mock test attempt completed successfully.",
        "final_results": final_score_details_structured
    }), 200

@app.route('/user/<int:user_id>/mock_test_attempts', methods=['GET'])
def get_user_mock_test_attempts(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        attempts = UserMockTestAttempt.query.filter_by(user_id=user_id).order_by(UserMockTestAttempt.start_time.desc()).all()

        attempts_data = []
        for attempt in attempts:
            test_title = "N/A"
            if attempt.mock_test:
                test_title = attempt.mock_test.title

            attempts_data.append({
                "attempt_id": attempt.id,
                "mock_test_id": attempt.mock_test_id,
                "mock_test_title": test_title,
                "start_time": attempt.start_time.isoformat() if attempt.start_time else None,
                "end_time": attempt.end_time.isoformat() if attempt.end_time else None,
                "status": attempt.status,
                "score_details": json.loads(attempt.score_details) if attempt.score_details else {}
            })
        return jsonify(attempts_data), 200
    except Exception as e:
        app.logger.error(f"Error fetching mock test attempts for user {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

# Vocabulary Builder Endpoints
@app.route('/wordlists', methods=['GET'])
def get_word_lists():
    try:
        lists = WordList.query.all()
        return jsonify([lst.to_dict() for lst in lists]), 200
    except Exception as e:
        app.logger.error(f"Error fetching word lists: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/wordlists/<int:list_id>/words', methods=['GET'])
def get_words_in_list(list_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    word_list = WordList.query.get_or_404(list_id)

    try:
        paginated_words = db.session.query(Word).join(word_to_word_list).filter(word_to_word_list.c.word_list_id == list_id).paginate(page=page, per_page=per_page, error_out=False)

        words_data = [word.to_dict() for word in paginated_words.items]

        return jsonify({
            "words": words_data,
            "total_pages": paginated_words.pages,
            "current_page": paginated_words.page,
            "total_words": paginated_words.total,
            "word_list_name": word_list.name
        }), 200
    except Exception as e:
        app.logger.error(f"Error fetching words for list {list_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/user/<int:user_id>/word_progress', methods=['POST'])
def update_user_word_progress(user_id):
    data = request.json
    word_id = data.get('word_id')
    status = data.get('status')

    if not word_id or not status:
        return jsonify({"error": "word_id and status are required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    word = Word.query.get(word_id)
    if not word:
        return jsonify({"error": "Word not found"}), 404

    progress = UserWordProgress.query.filter_by(user_id=user_id, word_id=word_id).first()

    try:
        if progress:
            progress.status = status
            progress.last_reviewed_at = datetime.utcnow()
            progress.review_count = (progress.review_count or 0) + 1
            if status == 'mastered':
                 progress.correct_count = (progress.correct_count or 0) + 1
            elif status == 'needs_review':
                 progress.incorrect_count = (progress.incorrect_count or 0) + 1
        else:
            progress = UserWordProgress(
                user_id=user_id,
                word_id=word_id,
                status=status,
                review_count=1
            )
            if status == 'mastered':
                 progress.correct_count = 1
            elif status == 'needs_review':
                 progress.incorrect_count = 1
            db.session.add(progress)

        db.session.commit()
        return jsonify(progress.to_dict()), 201 if not progress else 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating word progress for user {user_id}, word {word_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/user/<int:user_id>/vocabulary_summary', methods=['GET'])
def get_vocabulary_summary(user_id):
    user = User.query.get_or_404(user_id)
    try:
        total_words_interacted = UserWordProgress.query.filter_by(user_id=user_id).count()
        words_mastered = UserWordProgress.query.filter_by(user_id=user_id, status='mastered').count()
        words_learning = UserWordProgress.query.filter_by(user_id=user_id, status='learning').count()
        words_needs_review = UserWordProgress.query.filter_by(user_id=user_id, status='needs_review').count()

        return jsonify({
            "user_id": user_id,
            "total_words_interacted": total_words_interacted,
            "words_mastered": words_mastered,
            "words_learning": words_learning,
            "words_needs_review": words_needs_review
        }), 200
    except Exception as e:
        app.logger.error(f"Error fetching vocabulary summary for user {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/words/generate_example_sentence', methods=['POST'])
def generate_example_sentence_endpoint():
    data = request.json
    term = data.get('term')

    if not term:
        return jsonify({"error": "Term is required"}), 400

    try:
        example_sentence = gemini_service.generate_example_sentence_for_word(term)
        if "Could not generate" in example_sentence:
            return jsonify({"error": example_sentence, "term": term}), 500

        return jsonify({"term": term, "example_sentence": example_sentence}), 200
    except Exception as e:
        app.logger.error(f"Error in generate_example_sentence endpoint for term '{term}': {e}")
        return jsonify({"error": str(e), "term": term}), 500

@app.route('/user/<int:user_id>/progress_for_words', methods=['POST'])
def get_user_progress_for_words_batch(user_id):
    data = request.json
    word_ids = data.get('word_ids')

    if not isinstance(word_ids, list):
        return jsonify({"error": "word_ids must be a list"}), 400

    user = User.query.get_or_404(user_id)

    try:
        progress_records = UserWordProgress.query.filter(
            UserWordProgress.user_id == user_id,
            UserWordProgress.word_id.in_(word_ids)
        ).all()

        return jsonify([p.to_dict() for p in progress_records]), 200
    except Exception as e:
        app.logger.error(f"Error fetching batch word progress for user {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/words/add_to_list', methods=['POST'])
def add_words_to_list():
    data = request.json
    word_list_id = data.get('word_list_id')
    new_words_data = data.get('words')

    if not word_list_id or not new_words_data or not isinstance(new_words_data, list):
        return jsonify({"error": "word_list_id and a list of words (term, definition) are required"}), 400

    word_list = WordList.query.get(word_list_id)
    if not word_list:
        return jsonify({"error": "Word list not found"}), 404

    added_words_info = []
    for word_data in new_words_data:
        term = word_data.get('term')
        definition = word_data.get('definition')
        difficulty_level = word_data.get('difficulty_level', 'medium')

        if not term or not definition:
            added_words_info.append({"error": "Skipping word due to missing term or definition", "data": word_data})
            continue

        existing_word = Word.query.filter_by(term=term).first()
        if existing_word:
            if existing_word not in word_list.words:
                word_list.words.append(existing_word)
                added_words_info.append({"message": f"Added existing word '{term}' to list {word_list.name}", "word": existing_word.to_dict()})
            else:
                added_words_info.append({"message": f"Word '{term}' already in list {word_list.name}", "word": existing_word.to_dict()})
            continue

        example_sentence = word_data.get('example_sentence')
        if not example_sentence:
            try:
                generated_sentence = gemini_service.generate_example_sentence_for_word(term)
                if "Could not generate" in generated_sentence:
                    app.logger.warning(f"Could not auto-generate sentence for {term}: {generated_sentence}")
                    example_sentence = f"Example sentence for '{term}' could not be generated."
                else:
                    example_sentence = generated_sentence
            except Exception as e:
                app.logger.error(f"Error during sentence generation for {term}: {e}")
                example_sentence = f"Example sentence for '{term}' could not be generated due to an error."


        new_word = Word(
            term=term,
            definition=definition,
            example_sentence=example_sentence,
            difficulty_level=difficulty_level
        )
        db.session.add(new_word)
        word_list.words.append(new_word)
        added_words_info.append({"message": f"Added new word '{term}' to list {word_list.name}", "word": new_word.to_dict()})

    try:
        db.session.commit()
        return jsonify({"message": "Words processed successfully", "results": added_words_info}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding words to list {word_list_id}: {e}")
        return jsonify({"error": str(e), "results": added_words_info}), 500


# Essay Writing Assistant Endpoints
@app.route('/essay_topics', methods=['GET'])
def get_essay_topics():
    try:
        topics = EssayTopic.query.order_by(EssayTopic.created_at.desc()).all()
        return jsonify([topic.to_dict() for topic in topics]), 200
    except Exception as e:
        app.logger.error(f"Error fetching essay topics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/user/<int:user_id>/essays/submit', methods=['POST'])
def submit_user_essay(user_id):
    data = request.json
    essay_text = data.get('essay_text')
    essay_topic_id = data.get('essay_topic_id')
    essay_title = data.get('essay_title')

    if not essay_text:
        return jsonify({"error": "essay_text is required"}), 400

    user = User.query.get_or_404(user_id)
    topic_description = ""
    topic_title_for_submission = essay_title

    if essay_topic_id:
        essay_topic = EssayTopic.query.get(essay_topic_id)
        if essay_topic:
            topic_description = essay_topic.description
            if not topic_title_for_submission:
                topic_title_for_submission = essay_topic.title
        else:
            app.logger.warn(f"EssayTopic with id {essay_topic_id} not found, but submission will proceed without it.")

    if not topic_title_for_submission:
        topic_title_for_submission = "Untitled Essay"


    try:
        feedback_data = gemini_service.analyze_essay(essay_text, topic_description)

        if "error" in feedback_data:
            app.logger.error(f"Gemini essay analysis failed or returned partial data for user {user_id}. Raw: {feedback_data.get('raw_feedback_text', 'N/A')}")
            return jsonify({"error": feedback_data.get("general_comments") or feedback_data.get("error") or "Essay analysis failed"}), 500


        score_summary = feedback_data.get("overall_score", "N/A")
        if feedback_data.get("strengths") and len(feedback_data["strengths"]) > 0:
            score_summary += f" | Strengths: {', '.join(feedback_data['strengths'][:1])}"
        if feedback_data.get("areas_for_improvement") and len(feedback_data["areas_for_improvement"]) > 0:
            score_summary += f" | Improve: {', '.join(feedback_data['areas_for_improvement'][:1])}"


        new_submission = UserEssaySubmission(
            user_id=user_id,
            essay_topic_id=essay_topic_id,
            essay_title=topic_title_for_submission,
            essay_text=essay_text,
            feedback_json=json.dumps(feedback_data),
            score_summary=score_summary[:250]
        )
        db.session.add(new_submission)
        db.session.commit()

        return jsonify({
            "submission_id": new_submission.id,
            "feedback": feedback_data
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error submitting essay for user {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/user/<int:user_id>/essays', methods=['GET'])
def get_user_essays(user_id):
    User.query.get_or_404(user_id)
    try:
        submissions = UserEssaySubmission.query.filter_by(user_id=user_id)\
            .order_by(UserEssaySubmission.submission_date.desc()).all()
        return jsonify([s.to_dict() for s in submissions]), 200
    except Exception as e:
        app.logger.error(f"Error fetching essays for user {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/user/<int:user_id>/essays/<int:submission_id>', methods=['GET'])
def get_user_essay_submission_detail(user_id, submission_id):
    User.query.get_or_404(user_id)
    submission = UserEssaySubmission.query.filter_by(id=submission_id, user_id=user_id).first_or_404()

    try:
        return jsonify(submission.to_dict(include_full_text=True, include_full_feedback=True)), 200
    except Exception as e:
        app.logger.error(f"Error fetching essay submission {submission_id} for user {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

# Chat Endpoints
@app.route('/chat/start', methods=['POST'])
def start_chat():
    data = request.json
    user_id = data.get('user_id')
    user_profile_data = data.get('user_profile', {})

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(user_id)
    if not user:
        user_profile = {"learning_goals": [], "learning_style_preference": "any", "current_knowledge_level": {}, "preferences": {}}
    else:
        user_profile = user.to_dict()

    try:
        response = gemini_service.start_chat_session(user_id, user_profile)
        return jsonify(response), 200 if "message" in response else 500
    except Exception as e:
        app.logger.error(f"System Error: Failed to start chat: {e}")
        return jsonify({"error": f"System Error: Failed to start chat: {str(e)}"}), 500

@app.route('/chat/send_message', methods=['POST'])
def send_chat_message():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    user_profile_data = data.get('user_profile', {})

    if not user_id or not message:
        return jsonify({"error": "user_id and message are required"}), 400

    user = User.query.get(user_id)
    if not user:
        user_profile = {"learning_goals": [], "learning_style_preference": "any", "current_knowledge_level": {}, "preferences": {}}
    else:
        user_profile = user.to_dict()

    try:
        response = gemini_service.send_chat_message(user_id, message, user_profile)
        return jsonify(response), 200 if "ai_response" in response else 500
    except Exception as e:
        app.logger.error(f"System Error: Failed to send chat message: {e}")
        return jsonify({"error": f"System Error: Failed to send chat message: {str(e)}"}), 500

# Performance Analytics Endpoints
@app.route('/user/<int:user_id>/performance_trends', methods=['GET'])
def get_user_performance_trends(user_id):
    User.query.get_or_404(user_id)

    mock_test_attempts = UserMockTestAttempt.query.filter_by(user_id=user_id, status='completed')\
        .order_by(UserMockTestAttempt.start_time.asc()).all()

    overall_mock_test_scores = []
    section_mock_test_scores = {}

    for attempt in mock_test_attempts:
        if attempt.score_details:
            details = json.loads(attempt.score_details)
            date_str = attempt.start_time.strftime('%Y-%m-%d')

            overall_score_to_use = details.get('scaled_overall_score', details.get('overall_score_percentage'))
            if overall_score_to_use is not None:
                 overall_mock_test_scores.append({
                    "date": date_str,
                    "score": overall_score_to_use
                })

            if "sections" in details:
                for section_key, section_data in details["sections"].items():
                    section_title = section_key.replace("_", " ").title()
                    if section_title not in section_mock_test_scores:
                        section_mock_test_scores[section_title] = []

                    section_score_to_use = section_data.get('score_percentage')
                    if section_score_to_use is not None:
                        section_mock_test_scores[section_title].append({
                            "date": date_str,
                            "score": section_score_to_use
                        })

    question_attempts = QuestionAttempt.query.filter_by(user_id=user_id)\
        .order_by(QuestionAttempt.timestamp.asc()).all()

    topic_accuracy_over_time = {}

    daily_topic_performance = {}

    for qa in question_attempts:
        if qa.topic and qa.is_correct is not None:
            date_str = qa.timestamp.strftime('%Y-%m-%d')
            key = (date_str, qa.topic)
            if key not in daily_topic_performance:
                daily_topic_performance[key] = {"correct": 0, "total": 0}
            daily_topic_performance[key]["total"] += 1
            if qa.is_correct:
                daily_topic_performance[key]["correct"] += 1

    for (date_str, topic), data in daily_topic_performance.items():
        if topic not in topic_accuracy_over_time:
            topic_accuracy_over_time[topic] = []
        accuracy = (data["correct"] / data["total"]) * 100 if data["total"] > 0 else 0
        topic_accuracy_over_time[topic].append({
            "date": date_str,
            "accuracy": round(accuracy, 2)
        })
        topic_accuracy_over_time[topic].sort(key=lambda x: x['date'])


    return jsonify({
        "overall_mock_test_scores": overall_mock_test_scores,
        "section_mock_test_scores": section_mock_test_scores,
        "topic_accuracy_over_time": topic_accuracy_over_time
    }), 200

@app.route('/user/<int:user_id>/strengths_weaknesses', methods=['GET'])
def get_user_strengths_weaknesses(user_id):
    User.query.get_or_404(user_id)

    question_attempts = QuestionAttempt.query.filter_by(user_id=user_id).all()

    if not question_attempts:
        return jsonify({"strengths": [], "weaknesses": [], "message": "Not enough data for analysis."}), 200

    topic_performance = {}

    for qa in question_attempts:
        if qa.topic and qa.is_correct is not None:
            if qa.topic not in topic_performance:
                topic_performance[qa.topic] = {"correct": 0, "total": 0}
            topic_performance[qa.topic]["total"] += 1
            if qa.is_correct:
                topic_performance[qa.topic]["correct"] += 1

    if not topic_performance:
         return jsonify({"strengths": [], "weaknesses": [], "message": "No graded topic data available."}), 200

    MIN_QUESTIONS_THRESHOLD = 5
    analyzed_topics = []
    for topic, data in topic_performance.items():
        if data["total"] >= MIN_QUESTIONS_THRESHOLD:
            accuracy = (data["correct"] / data["total"]) * 100
            analyzed_topics.append({
                "topic": topic,
                "accuracy": round(accuracy, 2),
                "questions_answered": data["total"]
            })

    if not analyzed_topics:
        return jsonify({"strengths": [], "weaknesses": [], "message": f"Not enough questions answered per topic (min {MIN_QUESTIONS_THRESHOLD} required)."}), 200

    analyzed_topics.sort(key=lambda x: x["accuracy"], reverse=True)

    strengths = analyzed_topics[:3]
    weaknesses = analyzed_topics[-3:]
    weaknesses.reverse()

    return jsonify({
        "strengths": strengths,
        "weaknesses": weaknesses
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)