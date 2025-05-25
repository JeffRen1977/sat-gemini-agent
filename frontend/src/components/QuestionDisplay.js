// frontend/src/components/QuestionDisplay.js

import React from 'react';

function QuestionDisplay({ questionData, userAnswer, onAnswerChange, onSubmitAnswer, loading }) {
  if (!questionData || !questionData.question) {
    return <p>Loading question...</p>;
  }

  return (
    <div className="question-container">
      {/* Display Passage if it exists */}
      {questionData.passage && (
        <div className="reading-passage">
          <h3>Reading Passage:</h3>
          <p>{questionData.passage}</p>
          <hr />
        </div>
      )}

      <h3>Question:</h3>
      <p>{questionData.question}</p>

      {questionData.options && (
        <div className="options">
          {Object.entries(questionData.options).map(([key, value]) => (
            <div key={key}>
              <strong>{key})</strong> {value}
            </div>
          ))}
        </div>
      )}

      {/* This is the crucial part: ENSURE NO RENDERING OF CORRECT ANSWER OR EXPLANATION HERE */}
      {/* For example, remove any lines like: */}
      {/* {questionData.correctAnswer && <p>Correct Answer: {questionData.correctAnswer}</p>} */}
      {/* {questionData.explanation && <p>Explanation: {questionData.explanation}</p>} */}


      <div className="answer-input">
        <input
          type="text"
          value={userAnswer}
          onChange={(e) => onAnswerChange(e.target.value)}
          placeholder="Type your answer here (e.g., A, B, C, D or the value)"
          disabled={loading}
        />
        <button onClick={onSubmitAnswer} disabled={loading}>
          {loading ? 'Submitting...' : 'Submit Answer'}
        </button>
      </div>
    </div>
  );
}

export default QuestionDisplay;