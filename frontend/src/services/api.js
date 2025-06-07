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

// Performance Analytics API Functions
export const getUserPerformanceTrends = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/performance_trends`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch performance trends');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getUserPerformanceTrends:", error);
    throw error;
  }
};

export const getUserStrengthsWeaknesses = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/strengths_weaknesses`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch strengths and weaknesses');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getUserStrengthsWeaknesses:", error);
    throw error;
  }
};

// Essay Writing Assistant API Functions
export const getEssayTopics = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/essay_topics`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch essay topics');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getEssayTopics:", error);
    throw error;
  }
};

export const submitEssay = async (userId, essayData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/essays/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(essayData), // essayData is { essay_text, essay_topic_id?, essay_title? }
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to submit essay');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - submitEssay:", error);
    throw error;
  }
};

export const getUserEssays = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/essays`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch user essays');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getUserEssays:", error);
    throw error;
  }
};

export const getEssaySubmissionDetails = async (userId, submissionId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/essays/${submissionId}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch essay submission details');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getEssaySubmissionDetails:", error);
    throw error;
  }
};

// Vocabulary Builder API Functions
export const getWordLists = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/wordlists`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch word lists');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getWordLists:", error);
    throw error;
  }
};

export const getWordsForList = async (listId, page = 1, perPage = 10) => {
  try {
    const response = await fetch(`${API_BASE_URL}/wordlists/${listId}/words?page=${page}&per_page=${perPage}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch words for list');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getWordsForList:", error);
    throw error;
  }
};

export const updateUserWordProgress = async (userId, wordId, status) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/word_progress`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word_id: wordId, status }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to update word progress');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - updateUserWordProgress:", error);
    throw error;
  }
};

export const getUserVocabularySummary = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/vocabulary_summary`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch vocabulary summary');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getUserVocabularySummary:", error);
    throw error;
  }
};

export const generateExampleSentence = async (term) => {
  try {
    const response = await fetch(`${API_BASE_URL}/words/generate_example_sentence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ term }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to generate example sentence for ${term}`);
    }
    return response.json();
  } catch (error) {
    console.error("API Error - generateExampleSentence:", error);
    throw error;
  }
};

export const getUserProgressForWords = async (userId, wordIds) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/progress_for_words`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word_ids: wordIds }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch user progress for words');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getUserProgressForWords:", error);
    throw error;
  }
};

// Mock Test API Functions
export const getMockTests = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/mock_tests`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch mock tests');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getMockTests:", error);
    throw error;
  }
};

export const startMockTest = async (testId, userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/mock_tests/${testId}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to start mock test');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - startMockTest:", error);
    throw error;
  }
};

export const getMockTestSection = async (attemptId, sectionOrder) => {
  try {
    const response = await fetch(`${API_BASE_URL}/mock_tests/attempt/${attemptId}/section/${sectionOrder}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch mock test section');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getMockTestSection:", error);
    throw error;
  }
};

export const submitMockTestSection = async (attemptId, sectionOrder, userId, answers) => {
  try {
    const response = await fetch(`${API_BASE_URL}/mock_tests/attempt/${attemptId}/section/${sectionOrder}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, answers }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to submit mock test section');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - submitMockTestSection:", error);
    throw error;
  }
};

export const completeMockTest = async (attemptId, userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/mock_tests/attempt/${attemptId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to complete mock test');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - completeMockTest:", error);
    throw error;
  }
};

export const getUserMockTestAttempts = async (userId) => {
  try {
    // Note: This endpoint will be created in the backend as part of this subtask
    const response = await fetch(`${API_BASE_URL}/user/${userId}/mock_test_attempts`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch user mock test attempts');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getUserMockTestAttempts:", error);
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

export const getUserProfile = async (usernameOrId) => {
  try {
    const queryParam = typeof usernameOrId === 'number' ? `user_id=${usernameOrId}` : `username=${usernameOrId}`;
    const response = await fetch(`${API_BASE_URL}/user?${queryParam}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (response.status === 404) {
      return null;
    }
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get user profile');
    }
    return response.json();

  } catch (error) {
    console.error("API Error - getUserProfile:", error);
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

// NEW API FUNCTION: Start Chat Session
export const startChatSession = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to start chat session');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - startChatSession:", error);
    throw error;
  }
};

// NEW API FUNCTION: Send Chat Message
export const sendChatMessage = async (userId, message) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, message: message })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to send chat message');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - sendChatMessage:", error);
    throw error;
  }
};

// NEW API FUNCTION: Start Simulation Session (Step 8)
export const startSimulationSession = async (userId, simulationType) => {
  try {
    const response = await fetch(`${API_BASE_URL}/simulate/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, simulation_type: simulationType })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to start simulation session');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - startSimulationSession:", error);
    throw error;
  }
};

// NEW API FUNCTION: Send Simulation Message (Step 8)
export const sendSimulationMessage = async (userId, simulationType, userMessage, chatHistory) => {
  try {
    const response = await fetch(`${API_BASE_URL}/simulate/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, simulation_type: simulationType, user_message: userMessage, chat_history: chatHistory })
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to send simulation message');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - sendSimulationMessage:", error);
    throw error;
  }
};

// NEW API FUNCTION: Get User Achievements
export const getUserAchievements = async (userId) => {
  try {
    const url = `${API_BASE_URL}/user/achievements?user_id=${userId}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get user achievements');
    }
    return response.json();
  } catch (error) {
    console.error("API Error - getUserAchievements:", error);
    throw error;
  }
};