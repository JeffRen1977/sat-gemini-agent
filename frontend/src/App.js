// sat_gemini_agent/frontend/src/App.js

import React, { useState, useEffect, useRef } from 'react';
import {
  generateQuestion,
  evaluateAnswer,
  getStudyPlan,
  getPerformanceSummary,
  uploadImageQuestion,
  generateQuestionFromDatabase,
  manageUserProfile,
  getUserProfile,
  assessKnowledge,
  startChatSession,
  sendChatMessage,
  startSimulationSession,
  sendSimulationMessage,
  getUserAchievements,
  // Mock Test API Functions
  getMockTests,
  startMockTest,
  getMockTestSection,
  submitMockTestSection,
  completeMockTest,
  // Vocabulary API Functions (to be added to imports if not already there for other features)
  getWordLists,
  getWordsForList,
  updateUserWordProgress,
  getUserVocabularySummary,
  generateExampleSentence,
  getUserProgressForWords,
  // Essay API Functions
  getEssayTopics,
  submitEssay,
  getUserEssays,
  getEssaySubmissionDetails,
} from './services/api';
import { parseQuestionText } from './utils/dataParser';
import QuestionDisplay from './components/QuestionDisplay';
import MockTestList from './components/MockTestList';
import MockTestPlayer from './components/MockTestPlayer';
import FeedbackDisplay from './components/FeedbackDisplay';
import StudyPlanDisplay from './components/StudyPlanDisplay';
import WordListsDisplay from './components/WordListsDisplay';
import FlashcardView from './components/FlashcardView';
import ImageQuestionDisplay from './components/ImageQuestionDisplay';
import ChatInterface from './components/ChatInterface';
import SimulationComponent from './components/SimulationComponent';
import ProgressDashboard from './components/ProgressDashboard';
import EssayTopicsList from './components/EssayTopicsList'; // Import Essay Components
import EssayEditor from './components/EssayEditor';
import EssayFeedbackDisplay from './components/EssayFeedbackDisplay';
import UserEssaysDashboard from './components/UserEssaysDashboard';
import './App.css';

function App() {
  // --- USER STATE ---
  const [currentUserId, setCurrentUserId] = useState(null);
  const [username, setUsername] = useState('');
  const [userProfile, setUserProfile] = useState(null);
  const [initialKnowledgeInput, setInitialKnowledgeInput] = useState('');
  const [showChat, setShowChat] = useState(false); // NEW: State to control chat visibility

  // --- EXISTING QUESTION STATES ---
  const [questionText, setQuestionText] = useState(null);
  const [parsedQuestion, setParsedQuestion] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState('');
  const [studyPlan, setStudyPlan] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentTopic, setCurrentTopic] = useState('algebra word problems');
  const [currentDifficulty, setCurrentDifficulty] = useState('medium');
  const [startTime, setStartTime] = useState(null);

  // --- IMAGE QUESTION STATES ---
  const [selectedImages, setSelectedImages] = useState([]);
  const [imageDataUrls, setImageDataUrls] = useState([]);
  const [imageQuestionText, setImageQuestionText] = useState('');
  const [imageAnalysisResults, setImageAnalysisResults] = useState([]);


  const [showSimulation, setShowSimulation] = useState(false); // NEW: State for simulation visibility
  const [showProgress, setShowProgress] = useState(false);     // NEW: State for progress dashboard visibility

  // --- MOCK TEST STATES ---
  const [showMockTestList, setShowMockTestList] = useState(false);
  const [currentMockTest, setCurrentMockTest] = useState(null); // { testId: null }
  // const [activeMockTestAttemptId, setActiveMockTestAttemptId] = useState(null); // This seems unused, consider removing if MockTestPlayer handles its attemptId internally

  // --- VOCABULARY BUILDER STATES ---
  const [showVocabularyBuilder, setShowVocabularyBuilder] = useState(false);
  const [currentWordListId, setCurrentWordListId] = useState(null);
  const [currentWordListName, setCurrentWordListName] = useState('');

  // --- ESSAY WRITING ASSISTANT STATES ---
  const [showEssayTopics, setShowEssayTopics] = useState(false);
  const [showEssayEditor, setShowEssayEditor] = useState(false);
  const [showEssayFeedback, setShowEssayFeedback] = useState(false);
  const [showUserEssaysDashboard, setShowUserEssaysDashboard] = useState(false);
  const [currentEssayTopic, setCurrentEssayTopic] = useState(null); // Selected topic object
  const [currentEssaySubmissionData, setCurrentEssaySubmissionData] = useState(null); // { feedback, essayText, essayTitle }


  // --- DB QUESTION GENERATION STATE ---
  const [dbQueryTopic, setDbQueryTopic] = useState('');

  // --- EFFECT FOR INITIAL USER LOAD/REGISTRATION ---
  useEffect(() => {
    const storedUserId = localStorage.getItem('currentUserId');
    const storedUsername = localStorage.getItem('currentUsername');
    if (storedUserId && storedUsername) {
      setCurrentUserId(parseInt(storedUserId));
      setUsername(storedUsername);
      fetchUserProfile(parseInt(storedUserId));
    } else {
      console.log("No user found. Please enter a username to start or register.");
    }
  }, []);

  // --- NEW USER MANAGEMENT FUNCTIONS ---
  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
  };

  const handleRegisterOrLogin = async () => {
    if (!username.trim()) {
      alert("Please enter a username.");
      return;
    }
    setLoading(true);
    try {
      const existingUserResponse = await getUserProfile(username.trim());

      let user = null;
      if (existingUserResponse && existingUserResponse.user) {
          user = existingUserResponse.user;
      }

      if (user) {
        setCurrentUserId(user.id);
        setUserProfile(user);
        localStorage.setItem('currentUserId', user.id);
        localStorage.setItem('currentUsername', user.username);
        alert(`Welcome back, ${user.username}!`);
      } else {
        const newUserResponse = await manageUserProfile({ username: username.trim() });
        setCurrentUserId(newUserResponse.user.id);
        setUserProfile(newUserResponse.user);
        localStorage.setItem('currentUserId', newUserResponse.user.id);
        localStorage.setItem('currentUsername', newUserResponse.user.username);
        alert(`New user ${newUserResponse.user.username} registered!`);
      }
    } catch (error) {
      console.error("Error during register/login:", error);
      alert(`Failed to register/login: ${error.message}. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserProfile = async (userId) => {
    setLoading(true);
    try {
      const response = await getUserProfile(userId);
      if (response && response.user) {
        setUserProfile(response.user);
      } else {
        setUserProfile(null);
        console.warn(`User profile for ID ${userId} not found.`);
      }
    } catch (error) {
      console.error("Error fetching user profile:", error);
      setUserProfile(null);
    } finally {
      setLoading(false);
    }
  };

  // --- NEW KNOWLEDGE ASSESSMENT FUNCTION ---
  const handleAssessKnowledge = async () => {
    if (!currentUserId) {
      alert("Please log in or register a user first.");
      return;
    }
    if (!initialKnowledgeInput.trim()) {
      alert("Please describe your current knowledge or learning goals.");
      return;
    }
    setLoading(true);
    try {
      const response = await assessKnowledge(currentUserId, initialKnowledgeInput.trim());
      if (response.assessment) {
        setUserProfile(prevProfile => ({
          ...prevProfile,
          current_knowledge_level: response.assessment
        }));
        alert("Knowledge assessed and profile updated!");
        setInitialKnowledgeInput('');
      } else {
        alert("Failed to assess knowledge. Please try again.");
      }
    } catch (error) {
      console.error("Error assessing knowledge:", error);
      alert(`Failed to assess knowledge: ${error.message}. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  // --- MODIFIED EXISTING FUNCTIONS TO PASS userId ---
  const fetchNewQuestion = async (topic, difficulty, type = 'multiple_choice') => {
    if (!currentUserId) {
      alert("Please log in or register a user before generating questions.");
      return;
    }
    setLoading(true);
    setFeedback('');
    setStudyPlan('');
    setUserAnswer('');
    setImageAnalysisResults([]);
    setSelectedImages([]);
    setImageDataUrls([]);
    setImageQuestionText('');
    setDbQueryTopic('');

    setStartTime(Date.now());
    setCurrentTopic(topic);
    setCurrentDifficulty(difficulty);
    try {
      const data = await generateQuestion(topic, difficulty, type, currentUserId);
      setQuestionText(data.question);
      setParsedQuestion(parseQuestionText(data.question));
    } catch (error) {
      console.error("Error fetching question:", error);
      setQuestionText("Failed to load question. Please try again.");
      setParsedQuestion(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchQuestionFromDatabase = async () => {
    if (!currentUserId) {
      alert("Please log in or register a user before generating questions.");
      return;
    }
    if (!dbQueryTopic) {
      alert("Please enter a topic or keywords to query the database.");
      return;
    }

    setLoading(true);
    setFeedback('');
    setStudyPlan('');
    setUserAnswer('');
    setImageAnalysisResults([]);
    setSelectedImages([]);
    setImageDataUrls([]);
    setImageQuestionText('');
    setQuestionText(null);

    setStartTime(Date.now());
    setCurrentTopic(dbQueryTopic);
    setCurrentDifficulty('medium');

    try {
      const data = await generateQuestionFromDatabase(dbQueryTopic, currentDifficulty, 'multiple_choice', currentUserId);
      setQuestionText(data.question);
      setParsedQuestion(parseQuestionText(data.question));
    } catch (error) {
      console.error("Error fetching question from database:", error);
      setQuestionText(`Failed to load question from database: ${error.message}. Please try again.`);
      setParsedQuestion(null);
    } finally {
      setLoading(false);
    }
  };


  const handleSubmitAnswer = async () => {
    if (!currentUserId) {
      alert("Please log in or register a user before submitting answers.");
      return;
    }
    if (!parsedQuestion || !userAnswer) {
      alert("Please generate a question and provide an answer.");
      return;
    }

    setLoading(true);
    const timeTakenSeconds = Math.round((Date.now() - startTime) / 1000);

    try {
      const correct_answer_info = {
        answer: parsedQuestion.correctAnswer,
        explanation: parsedQuestion.explanation,
      };

      const feedbackData = await evaluateAnswer(
        questionText,
        userAnswer,
        correct_answer_info,
        currentTopic,
        currentDifficulty,
        timeTakenSeconds,
        currentUserId
      );
      setFeedback(feedbackData.feedback);

    } catch (error) {
      console.error("Error submitting answer:", error);
      setFeedback("Failed to get feedback. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGetStudyPlan = async () => {
    if (!currentUserId) {
      alert("Please log in or register a user to get a study plan.");
      return;
    }
    setLoading(true);
    try {
      const summaryResponse = await getPerformanceSummary(currentUserId);
      const userPerformanceData = summaryResponse.performance_data;

      if (Object.keys(userPerformanceData).length === 0) {
        setStudyPlan("No practice attempts recorded yet for this user to generate a study plan. Please answer some questions first!");
        return;
      }

      const data = await getStudyPlan(userPerformanceData, currentUserId);
      setStudyPlan(data.study_plan);
    } catch (error) {
      console.error("Error getting study plan:", error);
      setStudyPlan("Failed to generate study plan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitImageQuestion = async () => {
    if (!currentUserId) {
      alert("Please log in or register a user before analyzing images.");
      return;
    }
    if (imageDataUrls.length === 0 || !imageQuestionText) {
      alert("Please upload at least one image and type your question.");
      return;
    }

    setLoading(true);
    try {
      const result = await uploadImageQuestion(imageDataUrls, imageQuestionText, currentUserId);
      setImageAnalysisResults(result.aiResponses);
    } catch (error) {
      console.error("Error submitting image question:", error);
      setImageAnalysisResults([{ error: "Failed to analyze image question.", details: error.message }]);
    } finally {
      setLoading(false);
    }
  };

  const handleImageChange = (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) {
        setSelectedImages([]);
        setImageDataUrls([]);
        return;
    }

    setSelectedImages(files);
    setImageDataUrls([]);

    setQuestionText(null);
    setParsedQuestion(null);
    setFeedback(null);
    setImageAnalysisResults([]);
    setStudyPlan(null);
    setDbQueryTopic('');

    let loadedCount = 0;
    const newImageDataUrls = [];

    files.forEach((file) => {
        if (!file.type.startsWith('image/')) {
            alert(`File ${file.name} is not an image. Please select only image files.`);
            return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
            newImageDataUrls.push(reader.result);
            loadedCount++;
            if (loadedCount === files.length) {
                setImageDataUrls(newImageDataUrls);
            }
        };
        reader.readAsDataURL(file);
    });
  };

  return (
    <div className="App">
      <h1>SAT Gemini Agent</h1>

      {/* --- User Management Section --- */}
      <div className="user-management-section">
        <h2>User Profile</h2>
        {currentUserId ? (
          <div>
            <p>Logged in as: <strong>{username}</strong> (ID: {currentUserId})</p>
            {userProfile && (
              <div className="user-profile-details">
                <p><strong>Learning Goals:</strong> {userProfile.learning_goals && userProfile.learning_goals.join(', ')}</p>
                <p><strong>Learning Style:</strong> {userProfile.learning_style_preference}</p>
                <p>
                  <strong>Knowledge Level:</strong>
                  {userProfile.current_knowledge_level && Object.keys(userProfile.current_knowledge_level).length > 0 ? (
                    Object.entries(userProfile.current_knowledge_level).map(([topic, level]) => (
                      <span key={topic}>{topic}: {level} | </span>
                    ))
                  ) : 'Not assessed yet.'}
                </p>
                <p><strong>Preferences:</strong> {userProfile.preferences && JSON.stringify(userProfile.preferences)}</p>
              </div>
            )}
          </div>
        ) : (
          <div>
            <input
              type="text"
              placeholder="Enter username"
              value={username}
              onChange={handleUsernameChange}
              disabled={loading}
            />
            <button onClick={handleRegisterOrLogin} disabled={loading}>
              {loading ? 'Processing...' : 'Login / Register'}
            </button>
            <p>Enter a username to login or register a new profile.</p>
          </div>
        )}
      </div>

      {currentUserId && (
        <div className="knowledge-assessment-section">
          <h3>Assess Your Knowledge</h3>
          <textarea
            placeholder="Tell me about your current knowledge (e.g., 'I am strong in algebra but need help with reading comprehension main idea questions')."
            value={initialKnowledgeInput}
            onChange={(e) => setInitialKnowledgeInput(e.target.value)}
            rows="3"
            disabled={loading}
          ></textarea>
          <button onClick={handleAssessKnowledge} disabled={loading || !initialKnowledgeInput.trim()}>
            {loading ? 'Assessing...' : 'Assess My Knowledge'}
          </button>
        </div>
      )}
      <hr />
      {/* --- END User Management Section --- */}


      {/* NEW: Engagement & Gamification Buttons (Step 8 & 9) */}
      {currentUserId && ( // This condition must be met for the buttons to render
        <div className="engagement-buttons">
          <button onClick={() => setShowChat(!showChat)} disabled={loading}>
            {showChat ? 'Hide AI Tutor' : 'Chat with AI Tutor'}
          </button>
          <button onClick={() => setShowSimulation(!showSimulation)} disabled={loading}>
            {showSimulation ? 'Hide Simulation' : 'Start Simulated Practice'}
          </button>
          <button onClick={() => setShowProgress(!showProgress)} disabled={loading}>
            {showProgress ? 'Hide Progress' : 'View Progress & Achievements'}
          </button>
        </div>
      )}
      {/* END NEW */}

      
      {showChat && currentUserId && userProfile && (
        <ChatInterface
          userId={currentUserId}
          userProfile={userProfile}
          onClose={() => setShowChat(false)}
        />
      )}

      {showSimulation && currentUserId && (
        <SimulationComponent
          userId={currentUserId}
          onClose={() => setShowSimulation(false)}
        />
      )}

      {showProgress && currentUserId && (
        <ProgressDashboard
          userId={currentUserId}
          onClose={() => setShowProgress(false)}
        />
      )}

      {/* Mock Test Navigation */}
      {currentUserId && (
        <div className="mock-test-navigation">
          <button onClick={() => {
            setShowMockTestList(!showMockTestList);
            setCurrentMockTest(null); // Reset any active test player
            // Hide other major components if mock test list is shown
            if (!showMockTestList) {
              setShowChat(false);
              setShowSimulation(false);
              setShowProgress(false);
            }
          }} disabled={loading}>
            {showMockTestList ? 'Hide Mock Tests' : 'View Mock Tests'}
          </button>
          <button onClick={() => {
            setShowVocabularyBuilder(!showVocabularyBuilder);
            setCurrentWordListId(null); // Reset any active flashcard view
            // Hide other major components if vocab builder is shown
            if (!showVocabularyBuilder) {
              setShowChat(false);
              setShowSimulation(false);
              setShowProgress(false);
              setShowMockTestList(false);
              setCurrentMockTest(null);
              setShowEssayTopics(false); // Hide essay components
              setShowEssayEditor(false);
              setShowEssayFeedback(false);
              setShowUserEssaysDashboard(false);
            }
          }} disabled={loading}>
            {showVocabularyBuilder ? 'Hide Vocabulary Builder' : 'Vocabulary Builder'}
          </button>
          <button onClick={() => {
            setShowEssayTopics(!showEssayTopics || showEssayEditor || showEssayFeedback || showUserEssaysDashboard); // Toggle logic: show if any essay view is active, or toggle
            setShowEssayEditor(false);
            setShowEssayFeedback(false);
            setShowUserEssaysDashboard(false);
            setCurrentEssayTopic(null);
            setCurrentEssaySubmissionData(null);
             // Hide other major components
            if (!showEssayTopics) {
              setShowChat(false);
              setShowSimulation(false);
              setShowProgress(false);
              setShowMockTestList(false);
              setCurrentMockTest(null);
              setShowVocabularyBuilder(false);
              setCurrentWordListId(null);
            }
          }} disabled={loading}>
            Essay Practice
          </button>
        </div>
      )}

      {/* Conditional Rendering for Main Content vs Features */}
      {currentUserId && !showMockTestList && !currentMockTest && !showVocabularyBuilder && !currentWordListId && !showEssayTopics && !showEssayEditor && !showEssayFeedback && !showUserEssaysDashboard && (
         // This is the "main" view with regular practice questions, etc.
         // Only render this if no other major feature component is active.
        <>
          <h2>Text-Based Practice Questions (AI Generated)</h2>
          <button onClick={() => fetchNewQuestion('algebra word problems', 'medium', 'multiple_choice')} disabled={loading || !currentUserId}>
            {loading && !questionText ? 'Generating Math...' : 'Generate Math Question'}
          </button>
          <button onClick={() => fetchNewQuestion('reading comprehension', 'hard', 'multiple_choice')} disabled={loading || !currentUserId}>
            {loading && !questionText ? 'Generating Reading...' : 'Generate Reading Question'}
          </button>

          <hr />
          <h2>Generate Questions from Database (RAG)</h2>
      <div className="db-question-section">
        <textarea
          placeholder="Enter topic or keywords to find relevant content in the database (e.g., 'Pythagorean theorem', 'argumentative essays')"
          value={dbQueryTopic}
          onChange={(e) => setDbQueryTopic(e.target.value)}
          rows="2"
          disabled={loading || !currentUserId}
        ></textarea>
        <button onClick={fetchQuestionFromDatabase} disabled={loading || !dbQueryTopic || !currentUserId}>
          {loading ? 'Searching DB...' : 'Generate Question from DB'}
        </button>
      </div>

      {loading && (questionText || imageDataUrls.length > 0) && <p>Processing...</p>}

      {parsedQuestion && (
        <QuestionDisplay
          questionData={parsedQuestion}
          userAnswer={userAnswer}
          onAnswerChange={setUserAnswer}
          onSubmitAnswer={handleSubmitAnswer}
          loading={loading}
        />
      )}

      {feedback && (
        <FeedbackDisplay
          feedback={feedback}
          onNextQuestion={() => fetchNewQuestion(currentTopic, currentDifficulty)}
          loading={loading}
        />
      )}

      <h2>Image-Based Questions (Gemini Pro Vision)</h2>
      <div className="image-upload-section">
        <input type="file" accept="image/*" multiple onChange={handleImageChange} disabled={loading || !currentUserId} />
        {imageDataUrls.length > 0 && (
          <div className="image-previews-container">
            {imageDataUrls.map((url, index) => (
              <img key={index} src={url} alt={`Preview ${index + 1}`} style={{ maxWidth: '150px', maxHeight: '150px', margin: '5px', border: '1px solid #ccc' }} />
            ))}
          </div>
        )}
        <textarea
          placeholder="Type your question about ALL images here (e.g., 'Solve these math problems', 'Analyze these diagrams')."
          value={imageQuestionText}
          onChange={(e) => setImageQuestionText(e.target.value)}
          rows="3"
          disabled={loading || !currentUserId}
        ></textarea>
        <button onClick={handleSubmitImageQuestion} disabled={loading || imageDataUrls.length === 0 || !imageQuestionText || !currentUserId}>
          {loading ? 'Analyzing Images...' : 'Analyze Image Questions'}
        </button>
      </div>

      {imageAnalysisResults.length > 0 && (
        <div className="all-image-results">
            {imageAnalysisResults.map((analysis, index) => (
                <ImageQuestionDisplay key={index} analysis={analysis} />
            ))}
        </div>
      )}

      <hr />
      <h2>Personalized Study Plan</h2>
      <button onClick={handleGetStudyPlan} disabled={loading || !currentUserId}>
        Get Personalized Study Plan
      </button>

      {studyPlan && <StudyPlanDisplay studyPlan={studyPlan} />}
        </>
      )}

      {/* Mock Test Components */}
      {currentUserId && showMockTestList && !currentMockTest && (
        <MockTestList
          userId={currentUserId}
          onStartTest={(testId) => {
            setCurrentMockTest({ testId });
            setShowMockTestList(false);
          }}
        />
      )}
      {currentUserId && currentMockTest && (
        <MockTestPlayer
          testId={currentMockTest.testId}
          userId={currentUserId}
          onCompleteTest={(results) => {
            setCurrentMockTest(null);
            setShowMockTestList(true);
          }}
          onExitTest={() => {
            setCurrentMockTest(null);
            setShowMockTestList(true);
          }}
        />
      )}

      {/* Vocabulary Builder Components */}
      {currentUserId && showVocabularyBuilder && !currentWordListId && (
        <WordListsDisplay
          userId={currentUserId}
          onSelectList={(listId, listName) => {
            setCurrentWordListId(listId);
            setCurrentWordListName(listName || `Word List ${listId}`);
            setShowVocabularyBuilder(false);
          }}
        />
      )}
      {currentUserId && currentWordListId && (
        <FlashcardView
          listId={currentWordListId}
          userId={currentUserId}
          wordListName={currentWordListName}
          onExit={() => {
            setCurrentWordListId(null);
            setCurrentWordListName('');
            setShowVocabularyBuilder(true);
          }}
        />
      )}

      {/* Essay Writing Assistant Components */}
      {currentUserId && showEssayTopics && !showEssayEditor && !showEssayFeedback && !showUserEssaysDashboard && (
        <EssayTopicsList
          userId={currentUserId}
          onSelectTopic={(topic) => {
            setCurrentEssayTopic(topic);
            setShowEssayEditor(true);
            setShowEssayTopics(false);
          }}
          onStartOpenTopic={() => {
            setCurrentEssayTopic(null); // No specific topic
            setShowEssayEditor(true);
            setShowEssayTopics(false);
          }}
        />
      )}
      {currentUserId && showEssayEditor && (
        <EssayEditor
          userId={currentUserId}
          selectedTopic={currentEssayTopic}
          onSubmissionSuccess={(submissionId, feedback, essayText, essayTitle) => {
            setCurrentEssaySubmissionData({ submissionId, feedback, originalEssayText: essayText, essayTitle });
            setShowEssayEditor(false);
            setShowEssayFeedback(true);
          }}
          onCancel={() => {
            setShowEssayEditor(false);
            setShowEssayTopics(true); // Go back to topics list
            setCurrentEssayTopic(null);
          }}
        />
      )}
      {currentUserId && showEssayFeedback && currentEssaySubmissionData && (
        <EssayFeedbackDisplay
          feedback={currentEssaySubmissionData.feedback}
          originalEssayText={currentEssaySubmissionData.originalEssayText}
          essayTitle={currentEssaySubmissionData.essayTitle}
          onBackToList={() => { // This could lead to UserEssaysDashboard
            setShowEssayFeedback(false);
            setCurrentEssaySubmissionData(null);
            setShowUserEssaysDashboard(true); // Show the dashboard of all essays
            setShowEssayTopics(false); // Ensure topics list is hidden
          }}
          onWriteAnother={() => {
            setShowEssayFeedback(false);
            setCurrentEssaySubmissionData(null);
            setShowEssayTopics(true); // Go back to topics list to pick another or open topic
          }}
        />
      )}
       {currentUserId && showUserEssaysDashboard && (
        <UserEssaysDashboard
          userId={currentUserId}
          onSelectEssay={async (submissionId) => {
            setLoading(true);
            try {
              const details = await getEssaySubmissionDetails(currentUserId, submissionId);
              setCurrentEssaySubmissionData(details); // details should include feedback, essay_text, essay_title
              setShowUserEssaysDashboard(false);
              setShowEssayFeedback(true);
            } catch (err) {
              console.error("Error fetching submission details:", err);
              // Handle error, maybe show a notification
            } finally {
              setLoading(false);
            }
          }}
          onWriteNewEssay={() => {
            setShowUserEssaysDashboard(false);
            setCurrentEssayTopic(null);
            setShowEssayEditor(true);
          }}
        />
      )}

    </div>
  );
}

export default App;