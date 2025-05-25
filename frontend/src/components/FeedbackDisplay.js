// frontend/src/components/FeedbackDisplay.js

import React from 'react';

function FeedbackDisplay({ feedback, onNextQuestion, loading }) {
  if (!feedback) {
    return null;
  }

  // Check if feedback is an object (our new JSON response)
  const isJsonFeedback = typeof feedback === 'object' && feedback !== null;

  return (
    <div className="feedback-container">
      <h3>Feedback:</h3>
      {isJsonFeedback ? (
        <div>
          <h4>{feedback.feedback_summary}</h4>
          {feedback.personal_feedback && <p><strong>Personal Feedback:</strong> {feedback.personal_feedback}</p>}
          {feedback.explanation_comparison && <p><strong>Explanation Comparison:</strong> {feedback.explanation_comparison}</p>}
          {feedback.common_misconceptions && <p><strong>Common Misconceptions:</strong> {feedback.common_misconceptions}</p>}
          {feedback.correct_explanation_reiteration && <p><strong>Correct Explanation:</strong> {feedback.correct_explanation_reiteration}</p>}
          {feedback.next_steps_suggestion && <p><strong>Next Steps:</strong> {feedback.next_steps_suggestion}</p>}
          {feedback.error && <p style={{color: 'red'}}><strong>Error from AI:</strong> {feedback.error} {feedback.details}</p>}
        </div>
      ) : (
        // Fallback for old text-based feedback or AI parsing error
        <p>{feedback}</p>
      )}

      <button onClick={onNextQuestion} disabled={loading}>
        {loading ? 'Loading...' : 'Next Question'}
      </button>
    </div>
  );
}

export default FeedbackDisplay;