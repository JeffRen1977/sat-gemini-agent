// frontend/src/components/FeedbackDisplay.js

import React from 'react';

function FeedbackDisplay({ feedback, onNextQuestion, loading }) {
  if (!feedback) {
    return null;
  }

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

          {/* --- MODIFIED RENDERING FOR ARRAYS --- */}
          {feedback.correct_explanation_reiteration && feedback.correct_explanation_reiteration.length > 0 && (
            <div>
              <p><strong>Correct Explanation:</strong></p>
              <ol> {/* Using ordered list for steps */}
                {feedback.correct_explanation_reiteration.map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            </div>
          )}

          {feedback.next_steps_suggestion && feedback.next_steps_suggestion.length > 0 && (
            <div>
              <p><strong>Next Steps:</strong></p>
              <ul> {/* Using unordered list for suggestions */}
                {feedback.next_steps_suggestion.map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
          {/* --- END MODIFIED RENDERING --- */}

          {feedback.error && <p style={{color: 'red'}}><strong>Error from AI:</strong> {feedback.error} {feedback.details}</p>}
        </div>
      ) : (
        <p>{feedback}</p>
      )}

      <button onClick={onNextQuestion} disabled={loading}>
        {loading ? 'Loading...' : 'Next Question'}
      </button>
    </div>
  );
}

export default FeedbackDisplay;