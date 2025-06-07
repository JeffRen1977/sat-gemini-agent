import React, { useState, useEffect } from 'react';
import { getMockTests } from '../services/api';
import './MockTestList.css'; // Create this CSS file for styling

const MockTestList = ({ onStartTest, userId }) => {
  const [mockTests, setMockTests] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMockTests = async () => {
      try {
        setIsLoading(true);
        const data = await getMockTests();
        setMockTests(data);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to load mock tests.');
        setMockTests([]); // Clear any existing tests
      } finally {
        setIsLoading(false);
      }
    };

    fetchMockTests();
  }, []);

  if (isLoading) {
    return <p>Loading mock tests...</p>;
  }

  if (error) {
    return <p className="error-message">Error: {error}</p>;
  }

  if (mockTests.length === 0) {
    return <p>No mock tests available at the moment.</p>;
  }

  return (
    <div className="mock-test-list-container">
      <h2>Available Mock Tests</h2>
      {mockTests.map((test) => (
        <div key={test.id} className="mock-test-item">
          <h3>{test.title}</h3>
          <p>{test.description || 'No description available.'}</p>
          <p>Duration: {test.total_duration_minutes} minutes</p>
          {test.sections && test.sections.length > 0 && (
            <div className="mock-test-sections">
              <h4>Sections:</h4>
              <ul>
                {test.sections.map((section) => (
                  <li key={section.id}>
                    {section.title} ({section.duration_minutes} min) - Order: {section.order}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <button
            onClick={() => onStartTest(test.id, userId)}
            disabled={!userId}
            className="start-test-button"
          >
            Start Test
          </button>
          {!userId && <p className="login-prompt">Please log in to start a test.</p>}
        </div>
      ))}
    </div>
  );
};

export default MockTestList;
