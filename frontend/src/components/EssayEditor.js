import React, { useState, useEffect } from 'react';
import { submitEssay } from '../services/api';
import './EssayEditor.css';

const EssayEditor = ({ userId, selectedTopic, onSubmissionSuccess, onCancel }) => {
  const [essayTitle, setEssayTitle] = useState('');
  const [essayText, setEssayText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (selectedTopic) {
      setEssayTitle(selectedTopic.title || ''); // Pre-fill title if a topic is selected
      // You might want to pre-fill essayText with the topic description or a template
      // setEssayText(selectedTopic.description || '');
    } else {
      setEssayTitle(''); // Clear title for open topic
      setEssayText('');
    }
  }, [selectedTopic]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!essayText.trim()) {
      setError('Essay text cannot be empty.');
      return;
    }
    if (!userId) {
      setError('User not identified. Please log in again.');
      return;
    }

    setIsLoading(true);
    setError(null);

    const essayData = {
      essay_text: essayText,
      essay_topic_id: selectedTopic ? selectedTopic.id : null,
      essay_title: essayTitle || (selectedTopic ? selectedTopic.title : 'Untitled Essay'),
    };

    try {
      const result = await submitEssay(userId, essayData);
      if (result.submission_id && result.feedback) {
        onSubmissionSuccess(result.submission_id, result.feedback, essayText, essayData.essay_title);
      } else {
        throw new Error(result.error || 'Submission failed to return expected data.');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while submitting the essay.');
      setIsLoading(false); // Ensure loading is stopped on error
    }
    // setIsLoading(false); // Moved to finally or error catch if onSubmissionSuccess navigates away
  };

  return (
    <div className="essay-editor-container">
      <h2>{selectedTopic ? `Essay Topic: ${selectedTopic.title}` : 'Write Your Essay'}</h2>

      {selectedTopic && (
        <div className="selected-topic-prompt">
          <strong>Prompt:</strong>
          <p>{selectedTopic.description}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="essay-form">
        {!selectedTopic && ( // Only show title input if it's an open topic or they want to override
            <div className="form-group">
                <label htmlFor="essayTitle">Essay Title (Optional):</label>
                <input
                type="text"
                id="essayTitle"
                value={essayTitle}
                onChange={(e) => setEssayTitle(e.target.value)}
                placeholder="Enter your essay title"
                />
            </div>
        )}
         {selectedTopic && ( // If topic selected, show its title, but allow override if needed
            <div className="form-group">
                <label htmlFor="essayTitle">Essay Title:</label>
                <input
                type="text"
                id="essayTitle"
                value={essayTitle} // Pre-filled with topic title
                onChange={(e) => setEssayTitle(e.target.value)} // Allow user to change it
                placeholder="Confirm or update essay title"
                />
            </div>
        )}

        <div className="form-group">
          <label htmlFor="essayText">Your Essay:</label>
          <textarea
            id="essayText"
            value={essayText}
            onChange={(e) => setEssayText(e.target.value)}
            placeholder="Start writing your essay here..."
            rows="20" // Increased rows
            required
            disabled={isLoading}
          />
        </div>

        {error && <p className="error-message editor-error">{error}</p>}

        <div className="editor-actions">
          <button type="button" onClick={onCancel} className="cancel-button" disabled={isLoading}>
            Cancel
          </button>
          <button type="submit" className="submit-essay-button" disabled={isLoading}>
            {isLoading ? 'Submitting...' : 'Submit for Feedback'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EssayEditor;
