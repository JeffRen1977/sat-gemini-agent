import React, { useState, useEffect, useCallback } from 'react';
import { getWordsForList, updateUserWordProgress, generateExampleSentence, getUserProgressForWords } from '../services/api';
import './FlashcardView.css';

const FlashcardView = ({ listId, userId, onExit, wordListName }) => {
  const [words, setWords] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wordProgress, setWordProgress] = useState({}); // Map: word_id -> { status, ... }
  const [isGeneratingSentence, setIsGeneratingSentence] = useState(false);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalWordsInList, setTotalWordsInList] = useState(0);
  const perPage = 10; // Or make this configurable

  const fetchWordsAndProgress = useCallback(async (pageToLoad) => {
    if (!listId || !userId) {
      setError("List ID or User ID is missing.");
      setIsLoading(false);
      return;
    }
    try {
      setIsLoading(true);
      const wordsData = await getWordsForList(listId, pageToLoad, perPage);
      setWords(wordsData.words || []);
      setTotalPages(wordsData.total_pages || 1);
      setTotalWordsInList(wordsData.total_words || 0);
      setCurrentPage(wordsData.current_page || 1);
      setCurrentIndex(0); // Reset index when new words are loaded
      setIsFlipped(false);

      if (wordsData.words && wordsData.words.length > 0) {
        const wordIds = wordsData.words.map(w => w.id);
        const progressData = await getUserProgressForWords(userId, wordIds);
        const progressMap = {};
        (progressData || []).forEach(p => {
          progressMap[p.word_id] = p;
        });
        setWordProgress(progressMap);
      } else {
        setWordProgress({});
      }
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to load words or progress.');
      setWords([]);
      setWordProgress({});
    } finally {
      setIsLoading(false);
    }
  }, [listId, userId, perPage]);

  useEffect(() => {
    fetchWordsAndProgress(currentPage);
  }, [fetchWordsAndProgress, currentPage]);

  const handleFlip = () => setIsFlipped(!isFlipped);

  const handleNextWord = () => {
    if (currentIndex < words.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
    } else if (currentPage < totalPages) {
      // Load next page of words
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePrevWord = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsFlipped(false);
    } else if (currentPage > 1) {
      // Load previous page of words (and go to the last word of that page)
      // For simplicity, just loading previous page for now, user can navigate within it
      setCurrentPage(currentPage - 1);
      // Ideally, you'd set currentIndex to words.length-1 after new words load.
      // This might require an extra effect or careful state management.
    }
  };

  const handleUpdateStatus = async (wordId, status) => {
    if (!userId || !wordId) return;
    try {
      const updatedProgress = await updateUserWordProgress(userId, wordId, status);
      setWordProgress(prev => ({ ...prev, [wordId]: updatedProgress }));
    } catch (err) {
      setError(err.message || 'Failed to update word status.');
    }
  };

  const handleGenerateSentence = async (term, wordId) => {
    if (isGeneratingSentence) return;
    setIsGeneratingSentence(true);
    try {
      const response = await generateExampleSentence(term);
      setWords(currentWords =>
        currentWords.map(word =>
          word.id === wordId ? { ...word, example_sentence: response.example_sentence } : word
        )
      );
      setError(null); // Clear previous errors
    } catch (err) {
      setError(err.message || `Failed to generate sentence for ${term}.`);
    } finally {
      setIsGeneratingSentence(false);
    }
  };

  if (isLoading && words.length === 0) { // Show initial loading
    return <p className="loading-message">Loading flashcards...</p>;
  }

  if (error) {
    return <p className="error-message">Error: {error}</p>;
  }

  if (words.length === 0) {
    return (
      <div className="flashcard-view-container">
        <p>No words in this list or page.</p>
        <button onClick={onExit} className="exit-button">Exit</button>
      </div>
    );
  }

  const currentWord = words[currentIndex];
  const currentWordProg = wordProgress[currentWord.id];

  return (
    <div className="flashcard-view-container">
      <div className="flashcard-header">
        <h3>{wordListName || `Word List ${listId}`}</h3>
        <p>Word {currentIndex + 1 + (currentPage - 1) * perPage} of {totalWordsInList}</p>
        <button onClick={onExit} className="exit-button">Exit List</button>
      </div>

      <div className={`flashcard ${isFlipped ? 'flipped' : ''}`} onClick={handleFlip}>
        <div className="flashcard-inner">
          <div className="flashcard-front">
            <p className="term">{currentWord.term}</p>
            {currentWordProg && <span className="status-badge front-status">{currentWordProg.status}</span>}
          </div>
          <div className="flashcard-back">
            <p className="definition"><strong>Definition:</strong> {currentWord.definition}</p>
            {currentWord.example_sentence ? (
              <p className="example-sentence"><strong>Example:</strong> {currentWord.example_sentence}</p>
            ) : (
              <button
                onClick={(e) => { e.stopPropagation(); handleGenerateSentence(currentWord.term, currentWord.id); }}
                disabled={isGeneratingSentence}
                className="generate-sentence-button"
              >
                {isGeneratingSentence ? 'Generating...' : 'Generate Example'}
              </button>
            )}
            <div className="status-controls-back">
              <p>My Progress: {currentWordProg ? currentWordProg.status : 'New'}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flashcard-navigation">
        <button onClick={handlePrevWord} disabled={currentIndex === 0 && currentPage === 1}>Previous</button>
        <button onClick={handleNextWord} disabled={currentIndex === words.length - 1 && currentPage === totalPages}>Next</button>
      </div>

      <div className="status-update-buttons">
        <button onClick={() => handleUpdateStatus(currentWord.id, 'learning')} disabled={!userId}>Mark as Learning</button>
        <button onClick={() => handleUpdateStatus(currentWord.id, 'mastered')} disabled={!userId}>Mark as Mastered</button>
        <button onClick={() => handleUpdateStatus(currentWord.id, 'needs_review')} disabled={!userId}>Needs Review</button>
      </div>

      {isLoading && words.length > 0 && <p className="loading-message small-loading">Loading more words...</p>}
    </div>
  );
};

export default FlashcardView;
