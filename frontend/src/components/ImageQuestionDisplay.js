// frontend/src/components/ImageQuestionDisplay.js

import React from 'react';

function ImageQuestionDisplay({ analysis }) {
  if (!analysis) {
    return null;
  }

  const isSolutionArray = Array.isArray(analysis.ai_solution); // Check if it's an array

  return (
    <div className="image-analysis-container">
      <h3>AI Analysis & Solution:</h3>
      {analysis.ai_answer && (
        <p><strong>Concise Answer:</strong> {analysis.ai_answer}</p>
      )}
      {analysis.ai_solution && (
        <div>
          <p><strong>Detailed Solution/Explanation:</strong></p>
          {isSolutionArray ? (
            <ol> {/* Use ordered list if it's an array */}
              {analysis.ai_solution.map((step, index) => (
                <li key={index} style={{ whiteSpace: 'pre-wrap' }}>{step}</li> 
              ))}
            </ol>
          ) : (
            <p style={{ whiteSpace: 'pre-wrap' }}>{analysis.ai_solution}</p>
          )}
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