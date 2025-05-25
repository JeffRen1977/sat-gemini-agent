// frontend/src/App.js

import React, { useState, useEffect, useRef } from 'react'; // <--- IMPORT useRef for timer
import { generateQuestion, evaluateAnswer, getStudyPlan, saveAttempt, getPerformanceSummary } from './services/api'; // <--- IMPORT NEW API FUNCTIONS
import { parseQuestionText } from './utils/dataParser';
import QuestionDisplay from './components/QuestionDisplay';
import FeedbackDisplay from './components/FeedbackDisplay';
import StudyPlanDisplay from './components/StudyPlanDisplay';
import './App.css';

function App() {
  const [questionText, setQuestionText] = useState(null);
  const [parsedQuestion, setParsedQuestion] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState('');
  const [studyPlan, setStudyPlan] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentTopic, setCurrentTopic] = useState('algebra word problems'); // Track topic of current question
  const [currentDifficulty, setCurrentDifficulty] = useState('medium'); // Track difficulty
  const [startTime, setStartTime] = useState(null); // <--- NEW STATE FOR TIMER

  // No longer using userPerformance state for direct accumulation.
  // We'll fetch it from the backend before generating study plan.

  useEffect(() => {
    // Load initial question when component mounts
    fetchNewQuestion(currentTopic, currentDifficulty);
  }, []); // Empty dependency array means this runs once on mount

  const fetchNewQuestion = async (topic, difficulty, type = 'multiple_choice') => {
    setLoading(true);
    setFeedback(''); // Clear previous feedback
    setStudyPlan(''); // Clear study plan
    setUserAnswer(''); // Clear user answer
    setStartTime(Date.now()); // <--- START TIMER
    setCurrentTopic(topic); // Update current topic state
    setCurrentDifficulty(difficulty); // Update current difficulty state
    try {
      const data = await generateQuestion(topic, difficulty, type);
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

  const handleSubmitAnswer = async () => {
    if (!parsedQuestion || !userAnswer) {
      alert("Please generate a question and provide an answer.");
      return;
    }

    setLoading(true);
    const timeTakenSeconds = Math.round((Date.now() - startTime) / 1000); // <--- CALCULATE TIME TAKEN

    try {
      const correct_answer_info = {
        answer: parsedQuestion.correctAnswer,
        explanation: parsedQuestion.explanation,
      };

      const feedbackData = await evaluateAnswer(questionText, userAnswer, correct_answer_info);
      setFeedback(feedbackData.feedback); // feedbackData.feedback is now the JSON object from backend

      // =========================================================
      // NEW: Save Question Attempt to Database
      // =========================================================
      const isCorrect = feedbackData.feedback.is_correct; // Use is_correct from AI feedback
      const attemptData = {
        questionText: questionText,
        topic: currentTopic,
        difficulty: currentDifficulty,
        userAnswer: userAnswer,
        correctAnswer: parsedQuestion.correctAnswer,
        isCorrect: isCorrect,
        timeTakenSeconds: timeTakenSeconds,
        // userId: 'user123' // Add a real user ID if you implement authentication
      };
      await saveAttempt(attemptData); // Call the new API to save the attempt
      // =========================================================

    } catch (error) {
      console.error("Error submitting answer:", error);
      setFeedback("Failed to get feedback. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGetStudyPlan = async () => {
    setLoading(true);
    try {
      // =========================================================
      // NEW: Fetch aggregated performance data from backend first
      // =========================================================
      const summaryResponse = await getPerformanceSummary();
      const userPerformanceData = summaryResponse.performance_data; // Get the aggregated data

      if (Object.keys(userPerformanceData).length === 0) {
        setStudyPlan("No practice attempts recorded yet to generate a study plan. Please answer some questions first!");
        return;
      }
      // =========================================================

      const data = await getStudyPlan(userPerformanceData); // Pass the aggregated data to Gemini
      setStudyPlan(data.study_plan);
    } catch (error) {
      console.error("Error getting study plan:", error);
      setStudyPlan("Failed to generate study plan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>SAT Gemini Agent</h1>
      <button onClick={() => fetchNewQuestion('algebra word problems', 'medium', 'multiple_choice')} disabled={loading}>
        {loading && !questionText ? 'Generating Question...' : 'Generate Math Question'}
      </button>
      <button onClick={() => fetchNewQuestion('reading comprehension', 'hard', 'multiple_choice')} disabled={loading}>
        {loading && !questionText ? 'Generating Question...' : 'Generate Reading Question'}
      </button>

      {loading && questionText && <p>Processing...</p>}

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
          onNextQuestion={() => fetchNewQuestion(currentTopic, currentDifficulty)} // Next question can be same topic/difficulty
          loading={loading}
        />
      )}

      <button onClick={handleGetStudyPlan} disabled={loading}>
        Get Personalized Study Plan
      </button>

      {studyPlan && <StudyPlanDisplay studyPlan={studyPlan} />}
    </div>
  );
}

export default App;