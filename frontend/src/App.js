// frontend/src/App.js

import React, { useState, useEffect, useRef } from 'react';
import { generateQuestion, evaluateAnswer, getStudyPlan, saveAttempt, getPerformanceSummary, uploadImageQuestion } from './services/api'; // <--- IMPORT uploadImageQuestion
import { parseQuestionText } from './utils/dataParser';
import QuestionDisplay from './components/QuestionDisplay';
import FeedbackDisplay from './components/FeedbackDisplay';
import StudyPlanDisplay from './components/StudyPlanDisplay';
import ImageQuestionDisplay from './components/ImageQuestionDisplay'; // <--- NEW COMPONENT IMPORT
import './App.css';

function App() {
  // Existing states for text questions
  const [questionText, setQuestionText] = useState(null);
  const [parsedQuestion, setParsedQuestion] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState('');
  const [studyPlan, setStudyPlan] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentTopic, setCurrentTopic] = useState('algebra word problems');
  const [currentDifficulty, setCurrentDifficulty] = useState('medium');
  const [startTime, setStartTime] = useState(null);

  // =========================================================
  // NEW STATES FOR IMAGE UPLOAD
  // =========================================================
  const [selectedImage, setSelectedImage] = useState(null); // Stores the file object
  const [imageDataUrl, setImageDataUrl] = useState(null); // Stores Base64 data URL
  const [imageQuestionText, setImageQuestionText] = useState(''); // Text prompt for image
  const [imageAnalysisResult, setImageAnalysisResult] = useState(null); // Result from Gemini Vision Pro
  // =========================================================

  useEffect(() => {
    fetchNewQuestion(currentTopic, currentDifficulty);
  }, []);

  const fetchNewQuestion = async (topic, difficulty, type = 'multiple_choice') => {
    setLoading(true);
    setFeedback('');
    setStudyPlan('');
    setUserAnswer('');
    setImageAnalysisResult(null); // <--- Clear image results when generating text question
    setSelectedImage(null);
    setImageDataUrl(null);
    setImageQuestionText('');

    setStartTime(Date.now());
    setCurrentTopic(topic);
    setCurrentDifficulty(difficulty);
    try {
      const data = await generateQuestion(topic, difficulty, type);
      setQuestionText(data.question);
      setParsedQuestion(parseQuestionText(data.question));
    } catch (error) {
      console.error("Error fetching question:", error);
      setQuestionText("Failed to load question. Please try again.");
      setParsedQuestion(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!parsedQuestion || !userAnswer) {
      alert("Please generate a question and provide an answer.");
      return;
    }

    setLoading(true);
    const timeTakenSeconds = Math.round((Date.now() - startTime) / 1000);

    try {
      const correct_answer_info = {
        answer: parsedQuestion.correctAnswer,
        explanation: parsedQuestion.explanation,
      };

      const feedbackData = await evaluateAnswer(questionText, userAnswer, correct_answer_info);
      setFeedback(feedbackData.feedback);

      const isCorrect = feedbackData.feedback.is_correct;
      const attemptData = {
        questionText: questionText,
        topic: currentTopic,
        difficulty: currentDifficulty,
        userAnswer: userAnswer,
        correctAnswer: parsedQuestion.correctAnswer,
        isCorrect: isCorrect,
        timeTakenSeconds: timeTakenSeconds,
      };
      await saveAttempt(attemptData);

    } catch (error) {
      console.error("Error submitting answer:", error);
      setFeedback("Failed to get feedback. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGetStudyPlan = async () => {
    setLoading(true);
    try {
      const summaryResponse = await getPerformanceSummary();
      const userPerformanceData = summaryResponse.performance_data;

      if (Object.keys(userPerformanceData).length === 0) {
        setStudyPlan("No practice attempts recorded yet to generate a study plan. Please answer some questions first!");
        return;
      }

      const data = await getStudyPlan(userPerformanceData);
      setStudyPlan(data.study_plan);
    } catch (error) {
      console.error("Error getting study plan:", error);
      setStudyPlan("Failed to generate study plan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // NEW FUNCTIONS FOR IMAGE UPLOAD
  // =========================================================
  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImageDataUrl(reader.result); // Base64 data URL
      };
      reader.readAsDataURL(file); // Read file as Base64
      setQuestionText(null); // Clear text question display
      setParsedQuestion(null);
      setFeedback(null);
      setImageAnalysisResult(null); // Clear previous analysis results
      setStudyPlan(null); // Clear study plan
    } else {
      alert("Please select an image file.");
      setSelectedImage(null);
      setImageDataUrl(null);
    }
  };

  const handleSubmitImageQuestion = async () => {
    if (!imageDataUrl || !imageQuestionText) {
      alert("Please upload an image and type your question.");
      return;
    }

    setLoading(true);
    try {
      const result = await uploadImageQuestion(imageDataUrl, imageQuestionText);
      setImageAnalysisResult(result.aiResponse);
      // No immediate feedback or study plan update for image questions in this flow
    } catch (error) {
      console.error("Error submitting image question:", error);
      setImageAnalysisResult({ error: "Failed to analyze image question.", details: error.message });
    } finally {
      setLoading(false);
    }
  };
  // =========================================================


  return (
    <div className="App">
      <h1>SAT Gemini Agent</h1>

      {/* Text Question Generation */}
      <h2>Text-Based Practice Questions</h2>
      <button onClick={() => fetchNewQuestion('algebra word problems', 'medium', 'multiple_choice')} disabled={loading}>
        {loading && !questionText ? 'Generating Math...' : 'Generate Math Question'}
      </button>
      <button onClick={() => fetchNewQuestion('reading comprehension', 'hard', 'multiple_choice')} disabled={loading}>
        {loading && !questionText ? 'Generating Reading...' : 'Generate Reading Question'}
      </button>

      {loading && (questionText || imageDataUrl) && <p>Processing...</p>}

      {parsedQuestion && (
        <QuestionDisplay
          questionData={parsedQuestion}
          userAnswer={userAnswer}
          onAnswerChange={setUserAnswer}
          onSubmitAnswer={handleSubmitAnswer}
          loading={loading}
        />
      )}

      {feedback && (
        <FeedbackDisplay
          feedback={feedback}
          onNextQuestion={() => fetchNewQuestion(currentTopic, currentDifficulty)}
          loading={loading}
        />
      )}

      {/* Image Question Upload */}
      <h2>Image-Based Questions (Gemini Pro Vision)</h2>
      <div className="image-upload-section">
        <input type="file" accept="image/*" onChange={handleImageChange} disabled={loading} />
        {imageDataUrl && (
          <div className="image-preview">
            <img src={imageDataUrl} alt="Preview" style={{ maxWidth: '300px', maxHeight: '300px', border: '1px solid #ccc' }} />
          </div>
        )}
        <textarea
          placeholder="Type your question about the image here (e.g., 'Solve for x', 'What is the area of this shape?', 'Explain the graph')."
          value={imageQuestionText}
          onChange={(e) => setImageQuestionText(e.target.value)}
          rows="3"
          disabled={loading}
        ></textarea>
        <button onClick={handleSubmitImageQuestion} disabled={loading || !imageDataUrl || !imageQuestionText}>
          {loading ? 'Analyzing Image...' : 'Analyze Image Question'}
        </button>
      </div>

      {imageAnalysisResult && (
        <ImageQuestionDisplay analysis={imageAnalysisResult} />
      )}

      {/* Study Plan Section */}
      <hr />
      <h2>Personalized Study Plan</h2>
      <button onClick={handleGetStudyPlan} disabled={loading}>
        Get Personalized Study Plan
      </button>

      {studyPlan && <StudyPlanDisplay studyPlan={studyPlan} />}
    </div>
  );
}

export default App;