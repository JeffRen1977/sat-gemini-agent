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

        # Define a specific example for a reading question with clear delimiters
        READING_QUESTION_EXAMPLE = """
        ---BEGIN PASSAGE---
        The phenomenon of bioluminescence, the production of light by living organisms, is widespread in nature, particularly in marine environments. From the twinkling plankton in the ocean's surface to the deep-sea anglerfish with its glowing lure, bioluminescence serves various ecological functions, including attracting prey, defending against predators, and even communicating with conspecifics. While the chemical reactions involved vary among species, they generally involve a light-emitting molecule (luciferin) and an enzyme (luciferase) that catalyzes the reaction, consuming oxygen and ATP to produce light. This cold light, emitting less than 20% heat, is remarkably efficient compared to incandescent bulbs, which lose most energy as heat. The evolutionary pressures that led to such diverse and efficient light-producing mechanisms highlight the adaptive power of natural selection in response to environmental challenges.
        ---END PASSAGE---

        Question: Based on the passage, which of the following is NOT a function of bioluminescence mentioned in the text?
        A) Defense against predators
        B) Navigation in dark environments
        C) Attraction of prey
        D) Communication with other organisms of the same species
        Correct Answer: B  # <-- ADD THIS BACK
        Explanation: The passage explicitly mentions "attracting prey, defending against predators, and even communicating with conspecifics" as ecological functions. Navigation is not mentioned. # <-- ADD THIS BACK
        """

        # Define the general example format, now WITH Correct Answer and Explanation
        GENERAL_EXAMPLE_FORMAT = """
        Question: [Your question text here]
        A) Option A
        B) Option B
        C) Option C
        D) Option D
        Correct Answer: [Correct option letter or value] # <-- ADD THIS BACK
        Explanation: [Detailed explanation] # <-- ADD THIS BACK
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
        response = self.model.generate_content(prompt)

        # We'll parse the full response to extract Correct Answer and Explanation in dataParser.js
        # and these will be used for evaluation, but *not* displayed by QuestionDisplay.js
        return response.text


    def evaluate_and_explain(self, question, user_answer, correct_answer_info):
        # Define an example JSON output to guide the model
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
          ]
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

        EXAMPLE_JSON_OUTPUT:
        {EXAMPLE_JSON_OUTPUT}

        Ensure the output is valid JSON, enclosed in triple backticks, and contains only the JSON.
        """
        response = self.model.generate_content(prompt)
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