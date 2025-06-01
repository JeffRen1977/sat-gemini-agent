# backend/services/gemini_service.py

import google.generativeai as genai
import json  
import base64 
from io import BytesIO 
from PIL import Image
import pandas as pd # <--- IMPORT PANDAS
import re # <--- ADD THIS IMPORT

# Utility function to clean string before JSON parsing
# This regex matches any characters that are not allowed in JSON strings
# specifically, non-escaped control characters from U+0000 to U+001F (except tab, newline, carriage return)
# It also handles common Unicode non-breaking spaces if they cause issues.
_CLEAN_JSON_STRING_PATTERN = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\u0080-\u009F]') # ASCII control chars + some extended controls

def _clean_json_string(s):
    """Removes invalid control characters and other problematic chars from a string for JSON parsing."""
    return _CLEAN_JSON_STRING_PATTERN.sub('', s)

class GeminiService:
    def __init__(self, api_key, text_model_name='models/gemini-2.5-flash-preview-05-20', vision_model_name='gemini-pro-vision'):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        #genai.configure(api_key=api_key)
        self.text_model_name = text_model_name
        self.vision_model_name = vision_model_name # Store vision model name
        self.text_model = genai.GenerativeModel(self.text_model_name) # Use text_model
        self.vision_model = genai.GenerativeModel(self.vision_model_name) # <--- Initialize vision model


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
        response = self.text_model.generate_content(prompt)

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
        response = self.text_model.generate_content(prompt)
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
    
    # =========================================================
    # NEW METHOD: Analyze Image Question
    # =========================================================
    def analyze_image_question(self, image_base64_data, user_prompt_text):
        try:
            # Decode the base64 image data
            # image_base64_data will be 'data:image/png;base64,iVBORw0KGgoAAA...'
            # We need to strip the header and decode
            header, encoded = image_base64_data.split(",", 1)
            image_data_bytes = base64.b64decode(encoded)

            # Create PIL Image object from bytes
            img = Image.open(BytesIO(image_data_bytes))

            # Prepare the content for Gemini Vision Pro
            # The prompt is a list of parts: text and image
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

            response = self.vision_model.generate_content([vision_prompt_instructions, img, user_prompt_text]) # Send all parts
            text_response = response.text

            if text_response.startswith("```json") and text_response.endswith("```"):
                json_string = text_response[7:-3].strip()
            else:
                json_string = text_response.strip()

             # --- ADD THIS LINE TO CLEAN THE STRING ---
            json_string = _clean_json_string(json_string)
            # --- END ADDITION ---

            try:
                return json.loads(json_string)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from Gemini Vision: {e}")
                print(f"Raw Gemini Vision response: {text_response}")
                return {"error": "Failed to parse AI Vision response.", "details": str(e), "raw_response": text_response}

        except Exception as e:
            print(f"Error in analyze_image_question: {e}")
            return {"error": "Image analysis failed.", "details": str(e)}
    
    # --- ADD THIS NEW METHOD ---
    def list_available_models(self):
        print("--- Listing available Gemini Models ---")
        models_info = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models_info.append(f"  Name: {m.name}, Supported Methods: {m.supported_generation_methods}, Description: {m.description}")
        print("\n".join(models_info))
        print("-------------------------------------")

    # NEW METHOD: Generate SAT Question from Context
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