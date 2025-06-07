import React, { useState, useEffect, useCallback } from 'react';
import { startMockTest, getMockTestSection, submitMockTestSection, completeMockTest } from '../services/api';
import './MockTestPlayer.css'; // Create this CSS file for styling

// Basic Question Display Component (can be expanded or replaced)
const QuestionDisplay = ({ question, userAnswer, onAnswerChange }) => {
  if (!question || !question.question_text) { // Check if question or question_text is undefined
    return <p>Question loading or not available...</p>;
  }

  // Simple rendering for multiple choice questions
  // Assumes question.options is an array of strings
  // and question.correct_answer_info.answer might be the correct option text
  return (
    <div className="question-container">
      <h4>{question.question_text}</h4>
      {question.options && Array.isArray(question.options) ? (
        <div className="options-container">
          {question.options.map((option, index) => (
            <div key={index} className="option">
              <input
                type="radio"
                id={`${question.temp_id}_${index}`}
                name={question.temp_id}
                value={option}
                checked={userAnswer === option}
                onChange={(e) => onAnswerChange(question.temp_id, e.target.value)}
              />
              <label htmlFor={`${question.temp_id}_${index}`}>{option}</label>
            </div>
          ))}
        </div>
      ) : (
        <p>Question options are not in the expected format.</p>
      )}
      {/* For development: display correct answer info
      <details>
        <summary>Debug: Correct Answer Info</summary>
        <pre>{JSON.stringify(question.correct_answer_info, null, 2)}</pre>
      </details>
       */}
    </div>
  );
};


const MockTestPlayer = ({ testId, userId, onCompleteTest, onExitTest }) => {
  const [attemptId, setAttemptId] = useState(null);
  const [currentTestDetails, setCurrentTestDetails] = useState(null); // Store the whole test details
  const [currentSectionOrder, setCurrentSectionOrder] = useState(null);
  const [currentSectionData, setCurrentSectionData] = useState(null); // { title, duration, questions }
  const [userAnswers, setUserAnswers] = useState({}); // { temp_id_1: "answer1", temp_id_2: "answer2" }
  const [timeLeftInSection, setTimeLeftInSection] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [testResults, setTestResults] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadSection = useCallback(async (targetAttemptId, sectionOrderToLoad) => {
    try {
      setIsLoading(true);
      setError(null);
      const sectionData = await getMockTestSection(targetAttemptId, sectionOrderToLoad);
      setCurrentSectionData({
        title: sectionData.section_details.title,
        duration_minutes: sectionData.section_details.duration_minutes,
        questions: sectionData.questions || [], // Ensure questions is an array
      });
      setTimeLeftInSection(sectionData.section_details.duration_minutes * 60);
      setCurrentSectionOrder(sectionOrderToLoad);
      setUserAnswers({}); // Reset answers for the new section
      setIsLoading(false);
    } catch (err) {
      setError(err.message || `Failed to load section ${sectionOrderToLoad}.`);
      setIsLoading(false);
    }
  }, []);

  // Initialization
  useEffect(() => {
    const initializeTest = async () => {
      if (!testId || !userId) {
        setError("Test ID or User ID is missing.");
        setIsLoading(false);
        return;
      }
      try {
        setIsLoading(true);
        const startData = await startMockTest(testId, userId);
        setAttemptId(startData.attempt_id);
        setCurrentTestDetails(startData.first_section.mock_test); // Assuming mock_test details are nested if needed

        if (startData.first_section && startData.first_section.order) {
          await loadSection(startData.attempt_id, startData.first_section.order);
        } else {
          setError("Test has no sections or first section order is invalid.");
        }
      } catch (err) {
        setError(err.message || "Failed to start the mock test.");
      } finally {
        setIsLoading(false);
      }
    };
    initializeTest();
  }, [testId, userId, loadSection]);

  // Timer Logic
  useEffect(() => {
    if (timeLeftInSection <= 0 || !currentSectionData || testResults) {
      return () => {}; // No cleanup needed or already completed
    }

    const timerId = setInterval(() => {
      setTimeLeftInSection((prevTime) => prevTime - 1);
    }, 1000);

    if (timeLeftInSection === 1 && !isSubmitting) { // Submit a second before it hits 0 to avoid race conditions
        console.log("Time up! Submitting section...");
        handleSubmitSection(true); // autoSubmit = true
    }

    return () => clearInterval(timerId);
  }, [timeLeftInSection, currentSectionData, testResults, isSubmitting]);


  const handleAnswerChange = (questionTempId, answer) => {
    setUserAnswers((prevAnswers) => ({
      ...prevAnswers,
      [questionTempId]: answer,
    }));
  };

  const handleSubmitSection = useCallback(async (autoSubmit = false) => {
    if (isSubmitting || !attemptId || !currentSectionData || !currentSectionData.questions) return;

    setIsSubmitting(true);
    setError(null);

    const answersToSubmit = currentSectionData.questions.map(q => ({
      temp_id: q.temp_id, // Ensure temp_id is included
      question_text: q.question_text,
      user_answer: userAnswers[q.temp_id] || null, // Send null if unanswered
      correct_answer_info: q.correct_answer_info, // Send the original correct_answer_info
    }));

    try {
      const submissionResult = await submitMockTestSection(attemptId, currentSectionOrder, userId, answersToSubmit);
      // Optionally display section feedback here from submissionResult.detailed_feedback
      console.log("Section submitted:", submissionResult);


      if (submissionResult.next_section_order) {
        await loadSection(attemptId, submissionResult.next_section_order);
      } else {
        // Last section submitted, complete the test
        const completionResult = await completeMockTest(attemptId, userId);
        setTestResults(completionResult.final_results);
        if (onCompleteTest) {
          onCompleteTest(completionResult.final_results);
        }
      }
    } catch (err) {
      setError(err.message || "Failed to submit section.");
      if (autoSubmit) {
        // If auto-submit fails, maybe try to complete the test or show error
        console.error("Auto-submit failed:", err);
      }
    } finally {
      setIsSubmitting(false);
    }
  }, [attemptId, currentSectionOrder, userId, userAnswers, currentSectionData, loadSection, onCompleteTest, isSubmitting]);


  if (isLoading && !currentSectionData) { // Show initial loading for the whole test
    return <p className="loading-message">Loading test player...</p>;
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-message">Error: {error}</p>
        <button onClick={onExitTest || (() => window.location.reload())}>Return to List</button>
      </div>
    );
  }

  if (testResults) {
    return (
      <div className="test-results-container">
        <h2>Test Completed!</h2>
        <h3>Results:</h3>
        {testResults.overall_summary && (
          <div className="overall-summary">
            <h4>Overall Summary:</h4>
            <p>Total Correct: {testResults.overall_summary.total_correct} / {testResults.overall_summary.total_questions}</p>
            <p>Overall Percentage: {testResults.overall_summary.overall_percentage}%</p>
          </div>
        )}
        <h4>Section Scores:</h4>
        <ul>
          {Object.entries(testResults).map(([key, value]) => {
            if (key.startsWith("section_")) {
              return (
                <li key={key}>
                  {currentTestDetails?.sections?.find(s => `section_${s.order}` === key)?.title || key}: {value.score}%
                  ({value.correct_count}/{value.total_questions} correct)
                </li>
              );
            }
            return null;
          })}
        </ul>
        <button onClick={onExitTest || (() => window.location.reload())} className="action-button">
          View Dashboard or Try Another Test
        </button>
      </div>
    );
  }

  if (!currentSectionData) {
    return <p className="loading-message">Waiting for section data...</p>;
  }

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="mock-test-player-container">
      <div className="test-header">
        <h2>{currentTestDetails?.title || 'Mock Test'}</h2>
        <h3>Section: {currentSectionData.title}</h3>
        <p className="time-left">Time Left: {formatTime(timeLeftInSection)}</p>
      </div>

      {isLoading && <p className="loading-message">Loading questions...</p>}

      {!isLoading && currentSectionData.questions && currentSectionData.questions.length > 0 ? (
        currentSectionData.questions.map((q, index) => (
          <QuestionDisplay
            key={q.temp_id || index} // Use temp_id if available, otherwise index
            question={q}
            userAnswer={userAnswers[q.temp_id]}
            onAnswerChange={handleAnswerChange}
          />
        ))
      ) : (
        !isLoading && <p>No questions loaded for this section, or questions are malformed.</p>
      )}

      <button
        onClick={() => handleSubmitSection(false)}
        disabled={isSubmitting || isLoading}
        className="submit-section-button"
      >
        {isSubmitting ? 'Submitting...' : 'Submit Section'}
      </button>
      <button
        onClick={onExitTest || (() => window.location.reload())}
        className="exit-test-button"
        disabled={isSubmitting}
      >
        Exit Test
      </button>
    </div>
  );
};

export default MockTestPlayer;
