import React, { useState, useEffect } from 'react';
import { getWordLists } from '../services/api';
import './WordListsDisplay.css';

const WordListsDisplay = ({ onSelectList, userId }) => {
  const [wordLists, setWordLists] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLists = async () => {
      try {
        setIsLoading(true);
        const data = await getWordLists();
        setWordLists(data || []);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to load word lists.');
        setWordLists([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLists();
  }, []);

  if (isLoading) {
    return <p className="loading-message">Loading word lists...</p>;
  }

  if (error) {
    return <p className="error-message">Error: {error}</p>;
  }

  if (wordLists.length === 0) {
    return <p>No word lists available at the moment.</p>;
  }

  return (
    <div className="word-lists-container">
      <h2>Vocabulary Word Lists</h2>
      <ul className="word-list">
        {wordLists.map((list) => (
          <li key={list.id} className="word-list-item" onClick={() => userId ? onSelectList(list.id) : alert('Please log in to select a list.')}>
            <h3>{list.name}</h3>
            <p>{list.description || 'No description available.'}</p>
            <p className="word-count">Words: {list.word_count || 0}</p>
            {!userId && <span className="login-prompt-inline">(Login required)</span>}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default WordListsDisplay;
