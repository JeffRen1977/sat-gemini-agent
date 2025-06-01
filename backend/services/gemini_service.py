# backend/services/gemini_service.py

import google.generativeai as genai
import json  
import base64 
from io import BytesIO 
from PIL import Image
import pandas as pd
import re

# Utility function to clean string before JSON parsing
_CLEAN_JSON_STRING_PATTERN = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\u0080-\u009F]')

def _clean_json_string(s):
    """Removes invalid control characters and other problematic chars from a string for JSON parsing."""
    return _CLEAN_JSON_STRING_PATTERN.sub('', s)

class GeminiService:
    def __init__(self, api_key, text_model_name='models/gemini-2.5-flash-preview-05-20', vision_model_name='gemini-pro-vision'):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        #genai.configure(api_key=api_key) # This line is often part of global config, fine to keep it commented if configured elsewhere
        self.text_model_name = text_model_name
        self.vision_model_name = vision_model_name
        self.text_model = genai.GenerativeModel(self.text_model_name)
        self.vision_model = genai.GenerativeModel(self.vision_model_name)


    def generate_sat_question(self, topic, difficulty="medium", question_type="multiple_choice"):
        # This part remains mostly the same, but the prompt could eventually be
        # enhanced to consider user's learning style from their profile.
        # For now, we keep it as is, as the core change is the *assessment* method.
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
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from Gemini: {e}")
            print(f"Raw Gemini response: {text_response}")
            return {"error": "Failed to parse AI response. Please try again.", "details": str(e), "raw_response": text_response}

    def generate_study_plan(self, user_performance_data):
        # This method will be modified in a later step to also consider
        # the user's learning goals and knowledge level.
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

    # NEW METHOD: assess_knowledge
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