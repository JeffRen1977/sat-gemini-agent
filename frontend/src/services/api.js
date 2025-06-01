// sat_gemini_agent/frontend/src/services/api.js

const API_BASE_URL = process.env.REACT_APP_API_URL;

export const generateQuestion = async (topic, difficulty, questionType, userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate_question`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, difficulty, question_type: questionType, user_id: userId })
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

export const generateQuestionFromDatabase = async (queryTopic, difficulty, questionType, userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate_question_from_db`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_topic: queryTopic, difficulty, question_type: questionType, user_id: userId })
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

export const evaluateAnswer = async (questionText, userAnswer, correct_answer_info, topic, difficulty, timeTakenSeconds, userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/evaluate_answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_text: questionText,
        user_answer: userAnswer,
        correct_answer_info,
        topic,
        difficulty,
        timeTakenSeconds,
        user_id: userId
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

export const getStudyPlan = async (user_performance_data, userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/study_plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_performance_data, user_id: userId })
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

export const getPerformanceSummary = async (userId) => {
  try {
    const url = userId ? `${API_BASE_URL}/get_performance_summary?user_id=${userId}` : `${API_BASE_URL}/get_performance_summary`;
    const response = await fetch(url, {
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

export const uploadImageQuestion = async (imageDataUrls, userPromptText, userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/upload_image_question`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ imageDataUrls, userPromptText, user_id: userId })
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

export const manageUserProfile = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to manage user profile');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - manageUserProfile:", error);
    throw error;
  }
};

// MODIFIED API FUNCTION: Get User Profile
export const getUserProfile = async (usernameOrId) => {
  try {
    const queryParam = typeof usernameOrId === 'number' ? `user_id=${usernameOrId}` : `username=${usernameOrId}`;
    const response = await fetch(`${API_BASE_URL}/user?${queryParam}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    // --- MODIFIED LOGIC HERE ---
    if (response.status === 404) { // If user not found, return null instead of throwing error
      return null;
    }
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get user profile');
    }
    return response.json();
    // --- END MODIFIED LOGIC ---

  } catch (error) {
    console.error("API Error - getUserProfile:", error);
    // If it's a network error or other unhandled error, still re-throw
    throw error;
  }
};

export const assessKnowledge = async (userId, userInput, topicArea = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/assess_knowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, user_input: userInput, topic_area: topicArea })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to assess knowledge');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - assessKnowledge:", error);
    throw error;
  }
};