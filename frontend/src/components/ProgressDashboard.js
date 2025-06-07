// frontend/src/components/ProgressDashboard.js

import React, { useState, useEffect } from 'react';
import {
    getPerformanceSummary,
    getUserAchievements,
    getUserMockTestAttempts,
    getUserVocabularySummary,
    getUserPerformanceTrends, // Added
    getUserStrengthsWeaknesses // Added
} from '../services/api';
import './ProgressDashboard.css';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function ProgressDashboard({ userId, onClose }) {
  const [performanceData, setPerformanceData] = useState(null);
  const [achievements, setAchievements] = useState([]);
  // const [progressMetrics, setProgressMetrics] = useState(null); // This seems unused, can be removed or used if data is available
  const [mockTestAttempts, setMockTestAttempts] = useState([]);
  const [vocabularySummary, setVocabularySummary] = useState(null);
  const [performanceTrends, setPerformanceTrends] = useState(null); // Added
  const [strengthsWeaknesses, setStrengthsWeaknesses] = useState(null); // Added
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!userId) {
        setError("User ID is required to display progress.");
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const [
            performanceSummaryRes,
            userAchievementsRes,
            mockTestAttemptsRes,
            vocabSummaryRes,
            trendsRes, // Added
            strengthsWeaknessesRes // Added
        ] = await Promise.all([
          getPerformanceSummary(userId),
          getUserAchievements(userId),
          getUserMockTestAttempts(userId),
          getUserVocabularySummary(userId),
          getUserPerformanceTrends(userId), // Added
          getUserStrengthsWeaknesses(userId) // Added
        ]);

        setPerformanceData(performanceSummaryRes.performance_data);
        // setProgressMetrics(performanceSummaryRes.progress_metrics);
        setAchievements(userAchievementsRes.achievements);
        setMockTestAttempts(mockTestAttemptsRes || []);
        setVocabularySummary(vocabSummaryRes);
        setPerformanceTrends(trendsRes); // Added
        setStrengthsWeaknesses(strengthsWeaknessesRes); // Added

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

      {/*
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
      */}

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

      {/* New Section for Mock Test Performance */}
      <div className="dashboard-section">
        <h4>Mock Test Performance:</h4>
        {mockTestAttempts && mockTestAttempts.length > 0 ? (
          <ul className="mock-test-attempts-list">
            {mockTestAttempts.map((attempt) => (
              <li key={attempt.attempt_id} className="mock-test-attempt-item">
                <strong>{attempt.mock_test_title || `Test ID: ${attempt.mock_test_id}`}</strong>
                <p>Status: {attempt.status}</p>
                <p>Date: {new Date(attempt.start_time).toLocaleDateString()}</p>
                {attempt.status === 'completed' && attempt.score_details && attempt.score_details.overall_summary && (
                  <p>
                    Overall Score: {attempt.score_details.overall_summary.overall_percentage}%
                    ({attempt.score_details.overall_summary.total_correct} / {attempt.score_details.overall_summary.total_questions} correct)
                  </p>
                )}
                {/* Optionally, provide a link to view detailed results if available */}
              </li>
            ))}
          </ul>
        ) : (
          <p>No mock test attempts recorded yet.</p>
        )}
      </div>

      {/* Vocabulary Progress Section */}
      <div className="dashboard-section">
        <h4>Vocabulary Progress:</h4>
        {vocabularySummary ? (
          <ul>
            <li>Total Words Interacted With: {vocabularySummary.total_words_interacted}</li>
            <li>Words Mastered: {vocabularySummary.words_mastered}</li>
            <li>Words Learning: {vocabularySummary.words_learning}</li>
            <li>Words Needing Review: {vocabularySummary.words_needs_review}</li>
          </ul>
        ) : (
          <p>No vocabulary progress data available yet. Start learning some words!</p>
        )}
      </div>

      {/* Performance Trends Section */}
      <div className="dashboard-section">
        <h4>Performance Trends:</h4>
        {performanceTrends && performanceTrends.overall_mock_test_scores && performanceTrends.overall_mock_test_scores.length > 0 ? (
          <Line
            data={{
              labels: performanceTrends.overall_mock_test_scores.map(d => d.date),
              datasets: [{
                label: 'Overall Mock Test Score',
                data: performanceTrends.overall_mock_test_scores.map(d => d.score),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
              }]
            }}
            options={{ responsive: true, plugins: { title: { display: true, text: 'Overall Mock Test Score Trend' }}}}
          />
        ) : (
          <p>No overall mock test score trend data available.</p>
        )}
        {/* Add more charts for section scores and topic accuracy if needed */}
        {performanceTrends && performanceTrends.section_mock_test_scores && Object.keys(performanceTrends.section_mock_test_scores).map(sectionName => (
          performanceTrends.section_mock_test_scores[sectionName].length > 0 &&
            <div key={sectionName} style={{marginTop: '20px'}}>
                 <Line
                    data={{
                        labels: performanceTrends.section_mock_test_scores[sectionName].map(d => d.date),
                        datasets: [{
                            label: `${sectionName} Score Trend (%)`,
                            data: performanceTrends.section_mock_test_scores[sectionName].map(d => d.score),
                            borderColor: `rgb(${Math.floor(Math.random()*255)}, ${Math.floor(Math.random()*255)}, ${Math.floor(Math.random()*255)})`, // Random color for demo
                            tension: 0.1
                        }]
                    }}
                     options={{ responsive: true, plugins: { title: { display: true, text: `${sectionName} Score Trend` }}}}
                />
            </div>
        ))}
      </div>

      {/* Strengths and Weaknesses Section */}
      <div className="dashboard-section">
        <h4>Strengths & Weaknesses (Practice Questions):</h4>
        {strengthsWeaknesses ? (
          <>
            {strengthsWeaknesses.message && <p>{strengthsWeaknesses.message}</p>}
            {strengthsWeaknesses.strengths && strengthsWeaknesses.strengths.length > 0 && (
              <div>
                <h5>Top Performing Topics:</h5>
                <ul>
                  {strengthsWeaknesses.strengths.map(s => (
                    <li key={`strength-${s.topic}`}>{s.topic} (Accuracy: {s.accuracy}%, Answered: {s.questions_answered})</li>
                  ))}
                </ul>
              </div>
            )}
            {strengthsWeaknesses.weaknesses && strengthsWeaknesses.weaknesses.length > 0 && (
              <div style={{marginTop: '15px'}}>
                <h5>Topics to Focus On:</h5>
                <ul>
                  {strengthsWeaknesses.weaknesses.map(w => (
                    <li key={`weakness-${w.topic}`}>{w.topic} (Accuracy: {w.accuracy}%, Answered: {w.questions_answered})</li>
                  ))}
                </ul>
              </div>
            )}
          </>
        ) : (
          <p>Strength and weakness analysis not available yet.</p>
        )}
      </div>

    </div>
  );
}

export default ProgressDashboard;