// sat_gemini_agent/frontend/src/services/api.js

const API_BASE_URL = process.env.REACT_APP_API_URL;

export const generateQuestion = async (topic, difficulty, questionType) => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate_question`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, difficulty, question_type: questionType })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to generate question');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - generateQuestion:", error);
    throw error;
  }
};

// NEW API FUNCTION: Generate Question from Database
export const generateQuestionFromDatabase = async (queryTopic, difficulty, questionType) => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate_question_from_db`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_topic: queryTopic, difficulty, question_type: questionType })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to generate question from database');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - generateQuestionFromDatabase:", error);
    throw error;
  }
};

export const evaluateAnswer = async (questionText, userAnswer, correct_answer_info) => {
  try {
    const response = await fetch(`${API_BASE_URL}/evaluate_answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_text: questionText,
        user_answer: userAnswer,
        correct_answer_info
      })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to evaluate answer');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - evaluateAnswer:", error);
    throw error;
  }
};

export const getStudyPlan = async (user_performance_data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/study_plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_performance_data })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get study plan');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getStudyPlan:", error);
    throw error;
  }
};

export const saveAttempt = async (attemptData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/save_attempt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(attemptData)
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to save attempt');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - saveAttempt:", error);
  }
};

export const getPerformanceSummary = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/get_performance_summary`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get performance summary');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getPerformanceSummary:", error);
    throw error;
  }
};

export const uploadImageQuestion = async (imageDataUrls, userPromptText) => {
  try {
    const response = await fetch(`${API_BASE_URL}/upload_image_question`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ imageDataUrls, userPromptText })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to upload image question');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - uploadImageQuestion:", error);
    throw error;
  }
};