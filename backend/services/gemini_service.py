# backend/services/gemini_service.py

import google.generativeai as genai
import json
import base64
from io import BytesIO
from PIL import Image
import pandas as pd
import re

_CLEAN_JSON_STRING_PATTERN = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\u0080-\u009F]')

def _clean_json_string(s):
    """Removes invalid control characters and other problematic chars from a string for JSON parsing."""
    return _CLEAN_JSON_STRING_PATTERN.sub('', s)

class GeminiService:
    def __init__(self, api_key, text_model_name='models/gemini-2.5-flash-preview-05-20', vision_model_name='gemini-pro-vision'):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        self.text_model_name = text_model_name
        self.vision_model_name = vision_model_name
        self.text_model = genai.GenerativeModel(self.text_model_name)
        self.vision_model = genai.GenerativeModel(self.vision_model_name)
        # NEW: Store active chat sessions. For production, use a persistent store (e.g., Redis, database).
        self.active_chat_sessions = {} # Maps user_id to Gemini ChatSession objects


    def generate_sat_question(self, topic, difficulty="medium", question_type="multiple_choice"):
        READING_QUESTION_EXAMPLE = """
        ---BEGIN PASSAGE---
        The phenomenon of bioluminescence, the production of light by living organisms, is widespread in nature, particularly in marine environments. From the twinkling plankton in the ocean's surface to the deep-sea anglerfish with its glowing lure, bioluminescence serves various ecological functions, including attracting prey, defending against predators, and even communicating with conspecifics. While the chemical reactions involved vary among species, they generally involve a light-emitting molecule (luciferin) and an enzyme (luciferase) that catalyzes the reaction, consuming oxygen and ATP to produce light. This cold light, emitting less than 20% heat, is remarkably efficient compared to incandescent bulbs, which lose most energy as heat. The evolutionary pressures that led to such diverse and efficient light-producing mechanisms highlight the adaptive power of natural selection in response to environmental challenges.
        ---END PASSAGE---

        Question: Based on the passage, which of the following is NOT a function of bioluminescence mentioned in the text?
        A) Defense against predators
        B) Navigation in dark environments
        C) Attraction of prey
        D) Communication with other organisms of the same species
        Correct Answer: B
        Explanation: The passage explicitly mentions "attracting prey, defending against predators, and even communicating with conspecifics" as ecological functions. Navigation is not mentioned.
        """

        GENERAL_EXAMPLE_FORMAT = """
        Question: [Your question text here]
        A) Option A
        B) Option B
        C) Option C
        D) Option D
        Correct Answer: [Correct option letter or value]
        Explanation: [Detailed explanation]
        """

        prompt = f"""
        Generate a {difficulty} difficulty SAT-style {question_type} question on the topic of {topic}.

        **IMPORTANT:**
        - If the question_type is 'reading_comprehension', you MUST provide a short passage FIRST. The passage must be enclosed between '---BEGIN PASSAGE---' and '---END PASSAGE---'.
        - Then, after the passage, provide the multiple-choice question, followed by options, correct answer, and explanation.
        - For math questions, include necessary numbers and context.
        - For multiple-choice questions, provide 4 options (A, B, C, D) and clearly indicate the correct answer.

        EXAMPLE_FORMAT:
        {GENERAL_EXAMPLE_FORMAT}

        If the topic is 'reading comprehension' and question_type is 'multiple_choice',
        adhere strictly to this example structure, including the specific delimiters for the passage:
        {READING_QUESTION_EXAMPLE}
        """
        response = self.text_model.generate_content(prompt)
        return response.text


    def evaluate_and_explain(self, question, user_answer, correct_answer_info):
        EXAMPLE_JSON_OUTPUT = """
        {
          "is_correct": true,
          "feedback_summary": "Correct! Great job on this problem.",
          "personal_feedback": "You clearly understood the concept.",
          "explanation_comparison": "Your steps align perfectly with the standard solution.",
          "common_misconceptions": "Some students might misinterpret the wording.",
          "correct_explanation_reiteration": [
            "Step 1: Understand the core concept.",
            "Step 2: Apply the formula.",
            "Step 3: Calculate the result."
          ],
          "next_steps_suggestion": [
            "Practice 5 more problems of this type.",
            "Review related concepts in your textbook."
          ],
          "visual_aid_suggestion": "A bar chart showing the distribution of scores across different math topics."
        }
        """

        prompt = f"""
        You are an expert SAT tutor.
        Analyze the student's answer to the given SAT question.
        Provide feedback and explanations in a JSON format.

        SAT Question:
        {question}

        Student's Answer: {user_answer}

        Correct Answer: {correct_answer_info['answer']}
        Detailed Explanation for Correct Answer: {correct_answer_info['explanation']}

        Output should be a single JSON object with the following structure.
        For "correct_explanation_reiteration" and "next_steps_suggestion",
        each distinct step or suggestion should be a separate string element in the array.

        Additionally, consider if a visual aid (like a diagram, chart, or graph) would significantly help the student understand the concept better. If so, include a 'visual_aid_suggestion' field with a brief, clear text description of what that visual aid should depict. If not, omit this field.

        EXAMPLE_JSON_OUTPUT:
        {EXAMPLE_JSON_OUTPUT}

        Ensure the output is valid JSON, enclosed in triple backticks, and contains only the JSON.
        """
        response = self.text_model.generate_content(prompt)
        text_response = response.text
        if text_response.startswith("```json") and text_response.endswith("```"):
            json_string = text_response[7:-3].strip()
        else:
            json_string = text_response.strip()

        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from Gemini: {e}")
            print(f"Raw Gemini response: {text_response}")
            return {"error": "Failed to parse AI response. Please try again.", "details": str(e), "raw_response": text_response}

    def generate_study_plan(self, user_performance_data, user_profile):
        # ... (unchanged for this step) ...
        learning_goals = user_profile.get('learning_goals', [])
        learning_style = user_profile.get('learning_style_preference', 'any')
        knowledge_level = user_profile.get('current_knowledge_level', {})
        user_preferences = user_profile.get('preferences', {})

        goals_str = json.dumps(learning_goals) if learning_goals else "None specified."
        knowledge_str = json.dumps(knowledge_level, indent=2) if knowledge_level else "Not yet assessed."
        preferences_str = json.dumps(user_preferences) if user_preferences else "None specified."
        
        EXAMPLE_STUDY_PLAN_JSON = """
        {
          "summary": "Based on your performance and goals, here's a tailored study plan designed to maximize your SAT prep efficiency. You've shown strength in [Strong Area] but need to focus on [Weak Area].",
          "recommended_topics": [
            {
              "topic_name": "Algebra: Linear Equations",
              "reason": "Consistent 'needs practice' in recent attempts.",
              "suggested_resource_types": ["interactive exercises", "video tutorial", "diagrams"],
              "target_difficulty": "medium"
            },
            {
              "topic_name": "Reading: Main Idea Questions",
              "reason": "Lower accuracy in reading comprehension section, specifically main idea.",
              "suggested_resource_types": ["practice passages", "text-based explanations", "audio explanation"],
              "target_difficulty": "hard"
            }
          ],
          "practice_strategies": [
            "Dedicate 30 minutes daily to problems in your 'needs practice' areas.",
            "Review solutions for incorrect answers thoroughly, understanding *why* you made a mistake.",
            "Utilize timed practice tests weekly to build endurance and pacing."
          ],
          "study_tips": [
            "Break down complex topics into smaller, manageable chunks.",
            "Active recall: test yourself regularly without looking at notes.",
            "Ensure a consistent study schedule and adequate sleep for optimal performance."
          ],
          "motivational_message": "Every step you take is progress. Believe in your ability to master these challenges and achieve your SAT goals!"
        }
        """

        prompt = f"""
        You are an expert SAT study coach.
        Generate a personalized SAT study plan in JSON format based on the following student information:

        --- User Performance Data (Recent Attempts) ---
        {json.dumps(user_performance_data, indent=2)}

        --- User Profile ---
        Learning Goals: {goals_str}
        Learning Style Preference: {learning_style}
        Current Knowledge Level: {knowledge_str}
        User Preferences: {preferences_str}

        --- Instructions ---
        1. Analyze the performance data and knowledge level to identify strengths and weaknesses.
        2. Tailor the plan to the user's learning goals and preferred learning style. Specifically, for 'suggested_resource_types', select from "video tutorial", "interactive exercise", "diagrams", "text-based explanation", "audio explanation", "practice passages", "flashcards". Prioritize resource types that align with the user's '{learning_style}' learning style, but also suggest a variety.
        3. Provide specific, actionable recommendations.
        4. Focus on areas marked as 'needs practice' or where accuracy is low.
        5. For `recommended_topics`, each item should be an object with `topic_name`, a concise `reason` (linking to performance or knowledge level), `suggested_resource_types` (an array of strings), and `target_difficulty` ("easy", "medium", "hard").

        Output should be a single JSON object with the following structure.

        EXAMPLE JSON OUTPUT:
        {EXAMPLE_STUDY_PLAN_JSON}

        Ensure the output is valid JSON, enclosed in triple backticks, and contains only the JSON.
        """
        response = self.text_model.generate_content(prompt)
        text_response = response.text

        if text_response.startswith("```json") and text_response.endswith("```"):
            json_string = text_response[7:-3].strip()
        else:
            json_string = text_response.strip()

        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for study plan from Gemini: {e}")
            print(f"Raw Gemini response for study plan: {text_response}")
            return {"error": "Failed to parse AI study plan response. Please try again.", "details": str(e), "raw_response": text_response}

    def analyze_image_question(self, image_base64_data, user_prompt_text):
        try:
            header, encoded = image_base64_data.split(",", 1)
            image_data_bytes = base64.b64decode(encoded)
            img = Image.open(BytesIO(image_data_bytes))

            content = [
                user_prompt_text,
                img
            ]

            vision_prompt_instructions = """
            You are an expert SAT tutor. Analyze the provided image and the user's question about it.
            If the image contains a question (e.g., a math problem, a graph question), provide a clear, step-by-step solution and explanation.
            If the user's prompt is a direct question about the image's content, answer it directly and provide an explanation.
            If it's a multiple-choice question, identify the correct option.

            Output should be a single JSON object with the following structure:
            {
              "ai_answer": string, // A concise direct answer (e.g., "The correct answer is C", "x=5", or "The function is linear").
              "ai_solution": array of strings, // The full step-by-step solution or detailed explanation, with each step or distinct point as a separate string element in the array.
              "ai_confidence": string // Optional: "High", "Medium", "Low"
            }

            EXAMPLE_SOLUTION_ARRAY:
            [
              "Step 1: Identify the variables and given information from the image.",
              "Step 2: Formulate the equations or geometric properties.",
              "Step 3: Solve the equations/apply principles step-by-step.",
              "Step 4: State the final answer clearly."
            ]

            Ensure the output is valid JSON, enclosed in triple backticks, and contains only the JSON.
            """

            response = self.vision_model.generate_content([vision_prompt_instructions, img, user_prompt_text])
            text_response = response.text
            if text_response.startswith("```json") and text_response.endswith("```"):
                json_string = text_response[7:-3].strip()
            else:
                json_string = text_response.strip()

            json_string = _clean_json_string(json_string)

            try:
                return json.loads(json_string)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from Gemini Vision: {e}")
                print(f"Raw Gemini Vision response: {text_response}")
                return {"error": "Failed to parse AI Vision response.", "details": str(e), "raw_response": text_response}

        except Exception as e:
            print(f"Error in analyze_image_question: {e}")
            return {"error": "Image analysis failed.", "details": str(e)}

    def list_available_models(self):
        print("--- Listing available Gemini Models ---")
        models_info = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models_info.append(f"  Name: {m.name}, Supported Methods: {m.supported_generation_methods}, Description: {m.description}")
        print("\n".join(models_info))
        print("-------------------------------------")

    def assess_knowledge(self, user_id: str, user_input: str, topic_area: str = None):
        """
        Assesses a user's current knowledge based on their input, and returns
        a structured JSON of their knowledge level across various topics.
        """
        prompt = f"""
        You are an expert SAT tutor. Your task is to assess a student's current knowledge level
        in relevant SAT topics based on their provided input.

        The input can be a free-form description from the student (e.g., "I'm good at algebra but struggle with reading comprehension")
        or a summary of their performance on a diagnostic quiz.

        Based on the user's input, infer their proficiency in key SAT areas.
        If a specific topic area is provided, focus the assessment within that domain.

        Return your assessment as a single JSON object.
        The keys should be broad SAT topic areas (e.g., "Math: Algebra", "Math: Geometry", "Reading: Main Idea", "Writing: Grammar", etc.)
        and the values should be one of: "beginner", "intermediate", "advanced", or "needs practice".
        If a topic is not mentioned or cannot be inferred, you can omit it or mark as "unknown".

        User ID: {user_id}
        User Input: {user_input}
        {'Specific Topic Area to Focus On: ' + topic_area if topic_area else ''}

        EXAMPLE JSON OUTPUT:
        ```json
        {{
          "Math: Algebra": "intermediate",
          "Math: Geometry": "needs practice",
          "Reading: Main Idea": "advanced",
          "Writing: Essay Structure": "beginner",
          "Overall Aptitude": "intermediate"
        }}
        ```

        Ensure the output is valid JSON, enclosed in triple backticks, and contains only the JSON.
        """
        try:
            response = self.text_model.generate_content(prompt)
            text_response = response.text

            if text_response.startswith("```json") and text_response.endswith("```"):
                json_string = text_response[7:-3].strip()
            else:
                json_string = text_response.strip()

            json_string = _clean_json_string(json_string)

            return json.loads(json_string)
        except Exception as e:
            print(f"Error in assess_knowledge: {e}")
            return {"error": "Failed to assess knowledge.", "details": str(e)}

    def generate_sat_question_from_context(self, context_text: str, topic: str, difficulty: str, question_type: str):
        prompt = f"""
        You are an expert SAT question generator.
        Create a {difficulty} difficulty SAT-style {question_type} question based on the following context:

        ---BEGIN CONTEXT---
        {context_text}
        ---END CONTEXT---

        The question should be relevant to the topic of '{topic}'.
        
        **IMPORTANT:**
        - If the question_type is 'reading_comprehension', you MUST use the provided context as the passage, formatted within '---BEGIN PASSAGE---' and '---END PASSAGE---'.
        - For multiple-choice questions, provide 4 options (A, B, C, D) and clearly indicate the correct answer and a detailed explanation.

        EXAMPLE FORMAT:
        Question: [Your question text here]
        A) Option A
        B) Option B
        C) Option C
        D) Option D
        Correct Answer: [Correct option letter or value]
        Explanation: [Detailed explanation]

        Ensure the output is in the specified format.
        """
        response = self.text_model.generate_content(prompt)
        return response.text

    # NEW METHOD: start_chat_session
    def start_chat_session(self, user_id: int, user_profile: dict):
        """
        Starts a new chat session with the Gemini model for a specific user,
        setting up the tutor's persona based on user profile.
        Returns true if session started, false if already exists.
        """
        if user_id in self.active_chat_sessions:
            # Optionally clear existing chat history if starting a new one
            # self.active_chat_sessions[user_id] = self.text_model.start_chat(history=[])
            return {"message": "Chat session already active for this user."}
        
        # Prepare system instructions based on user profile
        learning_goals = user_profile.get('learning_goals', [])
        learning_style = user_profile.get('learning_style_preference', 'any')
        knowledge_level = user_profile.get('current_knowledge_level', {})
        
        system_instruction_prompt = f"""
        You are an incredibly supportive, knowledgeable, and patient SAT tutor.
        Your goal is to guide the student, clarify concepts, break down problems,
        identify misconceptions, and suggest effective learning strategies and resources.

        The student's profile indicates:
        - Learning Goals: {json.dumps(learning_goals)}
        - Learning Style Preference: {learning_style}
        - Current Knowledge Level: {json.dumps(knowledge_level, indent=2)}

        When responding, consider their learning style:
        - For 'visual' learners: Suggest diagrams, flowcharts, or visual examples.
        - For 'auditory' learners: Suggest verbal explanations, analogies, or thinking out loud.
        - For 'kinesthetic' learners: Suggest interactive problems, hands-on activities, or real-world applications.
        - For 'reading/writing' learners: Suggest detailed explanations, summaries, or practice writing.

        Always be encouraging and break down complex ideas into understandable parts.
        Do not give direct answers immediately; instead, guide them to the solution with hints or questions.
        If they ask for an explanation for a previously solved problem, explain it step by step.
        """
        
        # Start a new chat session with the model and store it
        self.active_chat_sessions[user_id] = self.text_model.start_chat(
            history=[],
            # Gemini 1.5 allows system_instruction in start_chat
            # For Gemini 2.5 flash, system_instruction might be less direct
            # and may need to be injected as the first message or implicit in the prompt
            # For this example, we'll assume it works implicitly via the context provided.
            # A more robust solution for system instructions would be to bake it into the initial prompt.
        )
        # For effective system instruction in continuous chat, it's often best to send a "system" message
        # or incorporate the persona strongly in the first AI response.
        # Here, we'll try to establish it in the general prompt for send_chat_message.

        print(f"Started new chat session for user {user_id}")
        return {"message": "Chat session started successfully!"}

    # NEW METHOD: send_chat_message
    def send_chat_message(self, user_id: int, message: str, user_profile: dict):
        """
        Sends a message to the active chat session for a user and gets a response.
        """
        chat_session = self.active_chat_sessions.get(user_id)
        if not chat_session:
            return {"error": "No active chat session found for this user. Please start a new session."}

        # Dynamically inject relevant user profile context for each turn,
        # especially for adaptive guidance. This is crucial for maintaining persona.
        learning_goals = user_profile.get('learning_goals', [])
        learning_style = user_profile.get('learning_style_preference', 'any')
        knowledge_level = user_profile.get('current_knowledge_level', {})

        # Craft the prompt for this turn, reminding the AI of its role and user context
        # This approach embeds the "system instruction" with each turn, which is robust
        # even if start_chat's system_instruction isn't fully utilized or persistent.
        turn_prompt = f"""
        You are an incredibly supportive, knowledgeable, and patient SAT tutor.
        Your goal is to guide the student, clarify concepts, break down problems,
        identify misconceptions, and suggest effective learning strategies and resources.

        The student's profile indicates:
        - Learning Goals: {json.dumps(learning_goals)}
        - Learning Style Preference: {learning_style}
        - Current Knowledge Level: {json.dumps(knowledge_level, indent=2)}

        When responding, consider their learning style:
        - For 'visual' learners: Suggest diagrams, flowcharts, or visual examples.
        - For 'auditory' learners: Suggest verbal explanations, analogies, or thinking out loud.
        - For 'kinesthetic' learners: Suggest interactive problems, hands-on activities, or real-world applications.
        - For 'reading/writing' learners: Suggest detailed explanations, summaries, or practice writing.

        Always be encouraging and break down complex ideas into understandable parts.
        Do not give direct answers immediately; instead, guide them to the solution with hints or questions.
        If they ask for an explanation for a previously solved problem, explain it step by step.

        Student's current message: {message}
        """

        try:
            # Use the .send_message method of the chat session
            # This maintains the conversation history internally for Gemini.
            response = chat_session.send_message(turn_prompt)
            return {"ai_response": response.text}
        except Exception as e:
            print(f"Error sending chat message for user {user_id}: {e}")
            return {"error": f"Failed to get AI response: {str(e)}"}
        

    def simulate_interview(self, user_id: int, simulation_type: str, user_input: str, chat_history: list = None):
        """
        Simulates an interactive interview or scenario-based learning session.
        """
        if chat_history is None:
            chat_history = []

        system_prompt = f"""
        You are an AI simulating a {simulation_type} for an SAT student.
        Your goal is to provide a realistic and challenging experience.
        Based on the user's input, respond as the interviewer or scenario-provider.
        Maintain context and guide the conversation.
        If the simulation type is 'SAT essay writing', prompt the user for essay responses and evaluate them.
        If the simulation type is 'college application interview', act as an interviewer.
        """
        
        full_prompt_parts = [{"role": "user", "parts": [system_prompt]}]
        for chat_item in chat_history:
            full_prompt_parts.append({"role": chat_item['role'], "parts": [chat_item['text']]})
        full_prompt_parts.append({"role": "user", "parts": [user_input]})

        try:
            response = self.text_model.generate_content(full_prompt_parts)
            return {"simulation_response": response.text}
        except Exception as e:
            print(f"Error in simulate_interview: {e}")
            return {"error": f"Failed to run simulation: {str(e)}"}