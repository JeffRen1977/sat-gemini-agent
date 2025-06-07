import React, { useState, useEffect } from 'react';
import { getEssayTopics } from '../services/api';
import './EssayTopicsList.css';

const EssayTopicsList = ({ onSelectTopic, onStartOpenTopic, userId }) => {
  const [topics, setTopics] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        setIsLoading(true);
        const data = await getEssayTopics();
        setTopics(data || []);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to load essay topics.');
        setTopics([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTopics();
  }, []);

  if (isLoading) {
    return <p className="loading-message">Loading essay topics...</p>;
  }

  if (error) {
    return <p className="error-message">Error: {error}</p>;
  }

  return (
    <div className="essay-topics-container">
      <h2>Essay Writing Practice</h2>
      <p className="topics-intro">Select a topic below to start writing, or choose an open topic.</p>

      <button
        onClick={onStartOpenTopic}
        className="open-topic-button"
        disabled={!userId}
      >
        Write on an Open Topic
      </button>
      {!userId && <p className="login-prompt-essay">Please log in to write an essay.</p>}

      {topics.length === 0 && !isLoading && (
        <p>No specific essay topics available at the moment. Try an open topic!</p>
      )}

      <div className="topics-list">
        {topics.map((topic) => (
          <div
            key={topic.id}
            className={`topic-item ${!userId ? 'disabled' : ''}`}
            onClick={() => userId ? onSelectTopic(topic) : alert('Please log in to select a topic.')}
          >
            <h3>{topic.title}</h3>
            <p className="topic-category">Category: {topic.category || 'General'}</p>
            <p className="topic-description">{topic.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EssayTopicsList;
