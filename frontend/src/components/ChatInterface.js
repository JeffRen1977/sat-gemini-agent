// frontend/src/components/ChatInterface.js

import React, { useState, useEffect, useRef } from 'react';
import { startChatSession, sendChatMessage } from '../services/api'; // Adjust path if needed
import './ChatInterface.css'; // We'll create this file next

function ChatInterface({ userId, userProfile, onClose }) {
  const [chatHistory, setChatHistory] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of chat history on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  useEffect(() => {
    if (userId && userProfile) {
      // Start chat session when component mounts and user is ready
      const initiateChat = async () => {
        setLoading(true);
        try {
          // You might want to explicitly pass userProfile to startChatSession here
          // if your backend requires it immediately for persona setup.
          // For now, the backend uses it from the DB based on userId.
          await startChatSession(userId);
          setChatHistory([{ sender: 'AI Tutor', text: "Hello! I'm your SAT AI tutor. How can I help you today?" }]);
        } catch (error) {
          console.error("Error starting chat session:", error);
          setChatHistory([{ sender: 'System Error', text: `Failed to start chat: ${error.message}` }]);
        } finally {
          setLoading(false);
        }
      };
      initiateChat();
    }
  }, [userId, userProfile]); // Re-run if user changes or profile loads

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || loading) return;

    const userMsg = { sender: 'You', text: currentMessage.trim() };
    setChatHistory((prevHistory) => [...prevHistory, userMsg]);
    setCurrentMessage('');
    setLoading(true);

    try {
      const response = await sendChatMessage(userId, userMsg.text);
      if (response.ai_response) {
        setChatHistory((prevHistory) => [
          ...prevHistory,
          { sender: 'AI Tutor', text: response.ai_response },
        ]);
      } else if (response.error) {
        setChatHistory((prevHistory) => [
          ...prevHistory,
          { sender: 'AI Tutor', text: `Error: ${response.error} ${response.details || ''}` },
        ]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setChatHistory((prevHistory) => [
        ...prevHistory,
        { sender: 'System Error', text: `Failed to send message: ${error.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { // Allow Shift+Enter for new line
      e.preventDefault(); // Prevent default new line behavior
      handleSendMessage();
    }
  };

  return (
    <div className="chat-interface-container">
      <div className="chat-header">
        <h3>SAT AI Tutor</h3>
        <button className="close-button" onClick={onClose}>X</button>
      </div>
      <div className="chat-messages">
        {chatHistory.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.sender === 'You' ? 'user-message' : 'ai-message'}`}>
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
        <div ref={messagesEndRef} /> {/* Scroll target */}
      </div>
      <div className="chat-input-area">
        <textarea
          value={currentMessage}
          onChange={(e) => setCurrentMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your question here..."
          rows="3"
          disabled={loading || !userId}
        />
        <button onClick={handleSendMessage} disabled={loading || !userId}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;