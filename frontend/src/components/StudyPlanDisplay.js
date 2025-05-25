// frontend/src/components/StudyPlanDisplay.js

import React from 'react';

function StudyPlanDisplay({ studyPlan }) {
  if (!studyPlan) {
    return null;
  }

  // Check if studyPlan is an object (our new JSON response)
  const isJsonStudyPlan = typeof studyPlan === 'object' && studyPlan !== null;

  return (
    <div className="study-plan-container">
      <h3>Your Personalized Study Plan:</h3>
      {isJsonStudyPlan ? (
        <div>
          {studyPlan.summary && <p><strong>Summary:</strong> {studyPlan.summary}</p>}

          {studyPlan.recommended_topics && studyPlan.recommended_topics.length > 0 && (
            <div>
              <h4>Recommended Topics:</h4>
              <ul>
                {studyPlan.recommended_topics.map((topic, index) => (
                  <li key={index}>{topic}</li>
                ))}
              </ul>
            </div>
          )}

          {studyPlan.practice_strategies && studyPlan.practice_strategies.length > 0 && (
            <div>
              <h4>Practice Strategies:</h4>
              <ul>
                {studyPlan.practice_strategies.map((strategy, index) => (
                  <li key={index}>{strategy}</li>
                ))}
              </ul>
            </div>
          )}

          {studyPlan.study_tips && studyPlan.study_tips.length > 0 && (
            <div>
              <h4>Study Tips:</h4>
              <ul>
                {studyPlan.study_tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>
          )}

          {studyPlan.motivational_message && <p><strong>Motivation:</strong> {studyPlan.motivational_message}</p>}
          {studyPlan.error && <p style={{color: 'red'}}><strong>Error from AI:</strong> {studyPlan.error} {studyPlan.details}</p>}
        </div>
      ) : (
        // Fallback for old text-based study plan or parsing error
        <p>{studyPlan}</p>
      )}
    </div>
  );
}

export default StudyPlanDisplay;