// frontend/src/components/ProgressDashboard.js

import React, { useState, useEffect } from 'react';
import { getPerformanceSummary, getUserAchievements } from '../services/api';
import './ProgressDashboard.css';

function ProgressDashboard({ userId, onClose }) {
  const [performanceData, setPerformanceData] = useState(null);
  const [achievements, setAchievements] = useState([]);
  const [progressMetrics, setProgressMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!userId) {
        setError("User ID is required to display progress.");
        setLoading(false);
        return;
      }
      try {
        const [performanceSummary, userAchievements] = await Promise.all([
          getPerformanceSummary(userId),
          getUserAchievements(userId)
        ]);

        setPerformanceData(performanceSummary.performance_data);
        setProgressMetrics(performanceSummary.progress_metrics);
        setAchievements(userAchievements.achievements);

      } catch (err) {
        console.error("Error fetching progress data:", err);
        setError(`Failed to load progress data: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]);

  if (loading) {
    return (
      <div className="progress-dashboard-container">
        <h3>Loading Progress...</h3>
        <button className="close-button" onClick={onClose}>X</button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="progress-dashboard-container">
        <h3>Error Loading Progress</h3>
        <p style={{ color: 'red' }}>{error}</p>
        <button className="close-button" onClick={onClose}>X</button>
      </div>
    );
  }

  return (
    <div className="progress-dashboard-container">
      <div className="dashboard-header">
        <h3>Your Learning Progress</h3>
        <button className="close-button" onClick={onClose}>X</button>
      </div>

      <div className="dashboard-section">
        <h4>Overall Performance:</h4>
        {performanceData && Object.keys(performanceData).length > 0 ? (
          <div>
            {Object.entries(performanceData).map(([category, topics]) => (
              <div key={category}>
                <h5>{category.charAt(0).toUpperCase() + category.slice(1)}:</h5>
                <ul>
                  {Object.entries(topics).map(([topicName, counts]) => (
                    <li key={topicName}>
                      {topicName}: Correct: {counts.correct}, Incorrect: {counts.incorrect}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (
          <p>No performance data available yet. Start answering some questions!</p>
        )}
      </div>

      <div className="dashboard-section">
        <h4>Key Progress Metrics:</h4>
        {progressMetrics && Object.keys(progressMetrics).length > 0 ? (
          <ul>
            {Object.entries(progressMetrics).map(([metricName, value]) => (
              <li key={metricName}>
                <strong>{metricName.replace(/_/g, ' ')}:</strong> {value}
              </li>
            ))}
          </ul>
        ) : (
          <p>No progress metrics available yet. Keep practicing!</p>
        )}
      </div>

      <div className="dashboard-section">
        <h4>Achievements:</h4>
        {achievements && achievements.length > 0 ? (
          <ul>
            {achievements.map((achievement, index) => (
              <li key={index}>
                <strong>{achievement.name}</strong>: {achievement.description} (Achieved on: {new Date(achievement.achieved_at).toLocaleDateString()})
              </li>
            ))}
          </ul>
        ) : (
          <p>No achievements unlocked yet. Keep up the good work!</p>
        )}
      </div>
    </div>
  );
}

export default ProgressDashboard;