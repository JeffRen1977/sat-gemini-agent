// frontend/src/components/SimulationComponent.js

import React, { useState, useEffect, useRef } from 'react';
import { startSimulationSession, sendSimulationMessage } from '../services/api';
import './ChatInterface.css';

function SimulationComponent({ userId, onClose }) {
  const [simulationHistory, setSimulationHistory] = useState([]);
  const [currentSimulationMessage, setCurrentSimulationMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [simulationType, setSimulationType] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [simulationHistory]);

  const handleStartSimulation = async (type) => {
    if (!userId) {
      alert("Please log in or register a user first.");
      return;
    }
    setLoading(true);
    setSimulationType(type);
    setSimulationHistory([]);
    try {
      const response = await startSimulationSession(userId, type);
      if (response.initial_response) {
        setSimulationHistory([{ sender: `Simulation (${type})`, text: response.initial_response }]);
      } else if (response.error) {
        setSimulationHistory([{ sender: 'System Error', text: `Failed to start simulation: ${response.error} ${response.details || ''}` }]);
      }
    } catch (error) {
      console.error("Error starting simulation:", error);
      setSimulationHistory([{ sender: 'System Error', text: `Failed to start simulation: ${error.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSendSimulationMessage = async () => {
    if (!currentSimulationMessage.trim() || loading || !simulationType) return;

    const userMsg = { sender: 'You', text: currentSimulationMessage.trim() };
    setSimulationHistory((prevHistory) => [...prevHistory, userMsg]);
    setCurrentSimulationMessage('');
    setLoading(true);

    try {
      const formattedHistory = simulationHistory.map(msg => ({
        role: msg.sender === 'You' ? 'user' : 'model',
        text: msg.text
      })).concat({ role: 'user', text: userMsg.text });


      const response = await sendSimulationMessage(userId, simulationType, userMsg.text, formattedHistory);
      if (response.simulation_response) {
        setSimulationHistory((prevHistory) => [
          ...prevHistory,
          { sender: `Simulation (${simulationType})`, text: response.simulation_response },
        ]);
      } else if (response.error) {
        setSimulationHistory((prevHistory) => [
          ...prevHistory,
          { sender: `Simulation (${simulationType}) Error`, text: `Error: ${response.error} ${response.details || ''}` },
        ]);
      }
    } catch (error) {
      console.error("Error sending simulation message:", error);
      setSimulationHistory((prevHistory) => [
        ...prevHistory,
        { sender: 'System Error', text: `Failed to send simulation message: ${error.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendSimulationMessage();
    }
  };

  return (
    <div className="chat-interface-container">
      <div className="chat-header">
        <h3>Simulated Practice: {simulationType || 'Select Type'}</h3>
        <button className="close-button" onClick={onClose}>X</button>
      </div>
      {!simulationType && (
        <div style={{ padding: '15px', textAlign: 'center' }}>
          <p>Choose a simulation type to begin:</p>
          <button onClick={() => handleStartSimulation('SAT essay writing')} disabled={loading}>
            {loading ? 'Loading...' : 'Start SAT Essay Practice'}
          </button>
          <button onClick={() => handleStartSimulation('college application interview')} disabled={loading}>
            {loading ? 'Loading...' : 'Start College Interview'}
          </button>
        </div>
      )}
      {simulationType && (
        <>
          <div className="chat-messages">
            {simulationHistory.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.sender === 'You' ? 'user-message' : 'ai-message'}`}>
                <strong>{msg.sender}:</strong> {msg.text}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <div className="chat-input-area">
            <textarea
              value={currentSimulationMessage}
              onChange={(e) => setCurrentSimulationMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Respond to the ${simulationType} prompt...`}
              rows="3"
              disabled={loading || !userId}
            />
            <button onClick={handleSendSimulationMessage} disabled={loading || !userId}>
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default SimulationComponent;