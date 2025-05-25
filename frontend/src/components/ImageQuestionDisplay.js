// frontend/src/components/ImageQuestionDisplay.js

import React from 'react';

function ImageQuestionDisplay({ analysis }) {
  if (!analysis) {
    return null;
  }

  return (
    <div className="image-analysis-container">
      <h3>AI Analysis & Solution:</h3>
      {analysis.ai_answer && (
        <p><strong>Concise Answer:</strong> {analysis.ai_answer}</p>
      )}
      {analysis.ai_solution && (
        <div>
          <p><strong>Detailed Solution/Explanation:</strong></p>
          <p style={{whiteSpace: 'pre-wrap'}}>{analysis.ai_solution}</p> {/* Use pre-wrap for preserving newlines */}
        </div>
      )}
      {analysis.ai_confidence && (
        <p><strong>AI Confidence:</strong> {analysis.ai_confidence}</p>
      )}
      {analysis.error && (
        <p style={{color: 'red'}}><strong>Error from AI:</strong> {analysis.error} {analysis.details}</p>
      )}
    </div>
  );
}

export default ImageQuestionDisplay;