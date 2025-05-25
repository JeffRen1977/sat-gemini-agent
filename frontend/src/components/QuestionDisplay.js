// frontend/src/components/QuestionDisplay.js

import React from 'react';

function QuestionDisplay({ questionData, userAnswer, onAnswerChange, onSubmitAnswer, loading }) {
  if (!questionData || !questionData.question) {
    return <p>Loading question...</p>;
  }

  return (
    <div className="question-container">
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