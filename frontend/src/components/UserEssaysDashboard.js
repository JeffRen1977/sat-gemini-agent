import React, { useState, useEffect } from 'react';
import { getUserEssays } from '../services/api';
import './UserEssaysDashboard.css';

const UserEssaysDashboard = ({ userId, onSelectEssay, onWriteNewEssay }) => {
  const [essays, setEssays] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) {
      setError("User ID is required to view essay dashboard.");
      setIsLoading(false);
      return;
    }

    const fetchEssays = async () => {
      try {
        setIsLoading(true);
        const data = await getUserEssays(userId);
        setEssays(data || []);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to load your essays.');
        setEssays([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEssays();
  }, [userId]);

  if (isLoading) {
    return <p className="loading-message">Loading your essays...</p>;
  }

  if (error) {
    return <p className="error-message">Error: {error}</p>;
  }

  return (
    <div className="user-essays-dashboard-container">
      <div className="dashboard-header">
        <h2>Your Essay Submissions</h2>
        <button onClick={onWriteNewEssay} className="write-new-essay-button">Write New Essay</button>
      </div>

      {essays.length === 0 ? (
        <p className="no-essays-message">You haven't submitted any essays yet. <span onClick={onWriteNewEssay} className="link-like">Start writing!</span></p>
      ) : (
        <ul className="essays-list">
          {essays.map((essay) => (
            <li
              key={essay.id}
              className="essay-item"
              onClick={() => onSelectEssay(essay.id)}
            >
              <div className="essay-item-header">
                <h3>{essay.essay_title || 'Untitled Essay'}</h3>
                <span className="essay-date">{new Date(essay.submission_date).toLocaleDateString()}</span>
              </div>
              <p className="essay-topic">
                Topic: {essay.essay_topic_title || 'Open Topic'}
              </p>
              <p className="essay-summary">
                Feedback Summary: {essay.score_summary || 'Not yet scored/summarized.'}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default UserEssaysDashboard;
