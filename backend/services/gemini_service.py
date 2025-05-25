# backend/services/gemini_service.py

import google.generativeai as genai
import json # <--- ADD THIS IMPORT
class GeminiService:
    def __init__(self, api_key, model_name='models/gemini-2.5-flash-preview-05-20'):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_sat_question(self, topic, difficulty="medium", question_type="multiple_choice"):
        prompt = f"""
        Generate a {difficulty} difficulty SAT-style {question_type} question on the topic of {topic}.
        For multiple-choice questions, provide 4 options (A, B, C, D) and clearly indicate the correct answer.
        For math questions, include necessary numbers and context.
        For reading questions, provide a short passage and then the question.
        Example format:

        Question: [Your question text here]
        A) Option A
        B) Option B
        C) Option C
        D) Option D
        Correct Answer: [Correct option letter or value]
        Explanation: [Detailed explanation]
        """
        response = self.model.generate_content(prompt)
        return response.text

    def evaluate_and_explain(self, question, user_answer, correct_answer_info):
        prompt = f"""
        You are an expert SAT tutor.
        Analyze the student's answer to the given SAT question.
        Provide feedback and explanations in a JSON format.

        SAT Question:
        {question}

        Student's Answer: {user_answer}

        Correct Answer: {correct_answer_info['answer']}
        Detailed Explanation for Correct Answer: {correct_answer_info['explanation']}

        Output should be a single JSON object with the following structure:
        {{
          "is_correct": boolean, // true if student's answer matches correct_answer_info['answer'] (case-insensitive, trimmed)
          "feedback_summary": string, // A short summary of the feedback (e.g., "Correct! Great job on algebra." or "Incorrect, review system of equations.")
          "personal_feedback": string, // Tailored encouraging feedback to the student based on their answer.
          "explanation_comparison": string, // Compares student's approach (if discernible) to the correct explanation.
          "common_misconceptions": string, // Explains common pitfalls related to this type of question.
          "correct_explanation_reiteration": string, // Reiteration or simplification of the provided correct explanation for the student.
          "next_steps_suggestion": string // Advice on what to study next based on their performance on this question.
        }}

        Ensure the output is valid JSON, enclosed in triple backticks, and contains only the JSON.
        """
        response = self.model.generate_content(prompt)
        # Attempt to parse the JSON. Gemini often wraps JSON in backticks.
        text_response = response.text
        if text_response.startswith("```json") and text_response.endswith("```"):
            json_string = text_response[7:-3].strip()
        else:
            json_string = text_response.strip()

        try:
            # We'll return the parsed JSON directly for the frontend to consume
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from Gemini: {e}")
            print(f"Raw Gemini response: {text_response}")
            # Fallback to a basic text response if JSON parsing fails
            return {"error": "Failed to parse AI response. Please try again.", "details": str(e), "raw_response": text_response}


    def generate_study_plan(self, user_performance_data):
        prompt = f"""
        You are an expert SAT study coach.
        A student has completed practice sessions with the following performance data:
        {json.dumps(user_performance_data, indent=2)}

        Based on these results, provide a personalized SAT study plan in JSON format.
        Focus on areas of weakness and suggest actionable strategies.

        Output should be a single JSON object with the following structure:
        {{
          "summary": string, // A brief, encouraging summary of their overall performance.
          "recommended_topics": [string], // A list of specific SAT topics to focus on (e.g., "Algebra: linear equations", "Reading: main idea", "Writing: subject-verb agreement").
          "practice_strategies": [string], // Actionable advice on how to practice (e.g., "Do 10 practice problems per day on recommended topics", "Review missed questions carefully").
          "study_tips": [string], // General study tips (e.g., "Practice under timed conditions", "Take breaks", "Review vocabulary daily").
          "motivational_message": string // An encouraging closing message.
        }}

        Ensure the output is valid JSON, enclosed in triple backticks, and contains only the JSON.
        """
        response = self.model.generate_content(prompt)
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
    
    # --- ADD THIS NEW METHOD ---
    def list_available_models(self):
        print("--- Listing available Gemini Models ---")
        models_info = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models_info.append(f"  Name: {m.name}, Supported Methods: {m.supported_generation_methods}, Description: {m.description}")
        print("\n".join(models_info))
        print("-------------------------------------")