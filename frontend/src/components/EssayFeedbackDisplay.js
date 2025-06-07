import React from 'react';
import './EssayFeedbackDisplay.css';

const EssayFeedbackDisplay = ({ feedback, originalEssayText, essayTitle, onBackToList, onWriteAnother }) => {
  if (!feedback) {
    return <p className="loading-message">Loading feedback...</p>;
  }
  if (feedback.error) {
    return (
        <div className="essay-feedback-container error-container">
            <h2>Feedback Error</h2>
            <p className="error-message">{feedback.error}</p>
            {feedback.details && <p>Details: {feedback.details}</p>}
            {feedback.raw_feedback_text && (
                <div className="raw-feedback-section">
                    <h4>Raw AI Response:</h4>
                    <pre>{feedback.raw_feedback_text}</pre>
                </div>
            )}
            <div className="feedback-actions">
                <button onClick={onBackToList || onWriteAnother} className="action-button">Try Again or Select Topic</button>
            </div>
        </div>
    );
  }


  return (
    <div className="essay-feedback-container">
      <div className="feedback-header">
        <h2>Essay Feedback</h2>
        {essayTitle && <h3>For: "{essayTitle}"</h3>}
      </div>

      <div className="feedback-section overall-score-section">
        <h4>Overall Score: {feedback.overall_score || 'Not Scored'}</h4>
      </div>

      {feedback.strengths && feedback.strengths.length > 0 && (
        <div className="feedback-section strengths-section">
          <h4>Strengths:</h4>
          <ul>
            {feedback.strengths.map((strength, index) => (
              <li key={`strength-${index}`}>{strength}</li>
            ))}
          </ul>
        </div>
      )}

      {feedback.areas_for_improvement && feedback.areas_for_improvement.length > 0 && (
        <div className="feedback-section improvements-section">
          <h4>Areas for Improvement:</h4>
          <ul>
            {feedback.areas_for_improvement.map((area, index) => (
              <li key={`improvement-${index}`}>{area}</li>
            ))}
          </ul>
        </div>
      )}

      {feedback.general_comments && (
        <div className="feedback-section general-comments-section">
            <h4>General Comments:</h4>
            <p>{feedback.general_comments}</p>
        </div>
      )}

      {feedback.detailed_feedback && feedback.detailed_feedback.length > 0 && (
        <div className="feedback-section detailed-categories-section">
          <h4>Detailed Feedback by Category:</h4>
          {feedback.detailed_feedback.map((categoryFeedback, index) => (
            <div key={`detail-${index}`} className="category-feedback-item">
              <h5>{categoryFeedback.category} (Score: {categoryFeedback.score || 'N/A'})</h5>
              <p>{categoryFeedback.comment}</p>
            </div>
          ))}
        </div>
      )}

      {originalEssayText && (
        <div className="feedback-section original-essay-section">
          <h4>Your Submitted Essay:</h4>
          <pre className="original-essay-text">{originalEssayText}</pre>
        </div>
      )}

      <div className="feedback-actions">
        {onBackToList && <button onClick={onBackToList} className="action-button">View All Essays</button>}
        {onWriteAnother && <button onClick={onWriteAnother} className="action-button primary">Write Another Essay</button>}
      </div>
    </div>
  );
};

export default EssayFeedbackDisplay;
