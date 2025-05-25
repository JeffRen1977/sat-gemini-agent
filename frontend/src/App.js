// frontend/src/App.js

import React, { useState, useEffect, useRef } from 'react';
import { generateQuestion, evaluateAnswer, getStudyPlan, saveAttempt, getPerformanceSummary, uploadImageQuestion } from './services/api';
import { parseQuestionText } from './utils/dataParser';
import QuestionDisplay from './components/QuestionDisplay';
import FeedbackDisplay from './components/FeedbackDisplay';
import StudyPlanDisplay from './components/StudyPlanDisplay';
import ImageQuestionDisplay from './components/ImageQuestionDisplay';
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
  // MODIFIED STATES FOR IMAGE UPLOAD (now for multiple images)
  // =========================================================
  const [selectedImages, setSelectedImages] = useState([]); // Stores array of file objects
  const [imageDataUrls, setImageDataUrls] = useState([]); // Stores array of Base64 data URLs
  const [imageQuestionText, setImageQuestionText] = useState('');
  const [imageAnalysisResults, setImageAnalysisResults] = useState([]); // Stores array of results for each image
  // =========================================================

  useEffect(() => {
    fetchNewQuestion(currentTopic, currentDifficulty);
  }, []);

  const fetchNewQuestion = async (topic, difficulty, type = 'multiple_choice') => {
    setLoading(true);
    setFeedback('');
    setStudyPlan('');
    setUserAnswer('');
    setImageAnalysisResults([]); // <--- Clear image results when generating text question
    setSelectedImages([]); // <--- Clear selected images
    setImageDataUrls([]); // <--- Clear image data URLs
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
  // MODIFIED FUNCTIONS FOR IMAGE UPLOAD (now for multiple images)
  // =========================================================
  const handleImageChange = (event) => {
    const files = Array.from(event.target.files); // Convert FileList to Array
    if (files.length === 0) {
        setSelectedImages([]);
        setImageDataUrls([]);
        return;
    }

    setSelectedImages(files);
    setImageDataUrls([]); // Clear previous URLs

    // Clear text question display and analysis results
    setQuestionText(null);
    setParsedQuestion(null);
    setFeedback(null);
    setImageAnalysisResults([]);
    setStudyPlan(null);

    let loadedCount = 0;
    const newImageDataUrls = [];

    files.forEach((file) => {
        if (!file.type.startsWith('image/')) {
            alert(`File ${file.name} is not an image. Please select only image files.`);
            // You might want to filter out non-images or stop processing here
            return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
            newImageDataUrls.push(reader.result); // Add Base64 data URL
            loadedCount++;
            if (loadedCount === files.length) {
                setImageDataUrls(newImageDataUrls);
            }
        };
        reader.readAsDataURL(file); // Read file as Base64
    });
  };

  const handleSubmitImageQuestion = async () => {
    if (imageDataUrls.length === 0 || !imageQuestionText) {
      alert("Please upload at least one image and type your question.");
      return;
    }

    setLoading(true);
    try {
      // Send an array of imageDataUrls to the backend
      const result = await uploadImageQuestion(imageDataUrls, imageQuestionText);
      setImageAnalysisResults(result.aiResponses); // Backend will return an array of responses
    } catch (error) {
      console.error("Error submitting image question:", error);
      setImageAnalysisResults([{ error: "Failed to analyze image question.", details: error.message }]);
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

      {loading && (questionText || imageDataUrls.length > 0) && <p>Processing...</p>} {/* Adjust loading condition */}

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
        <input type="file" accept="image/*" multiple onChange={handleImageChange} disabled={loading} /> {/* <--- ADD multiple ATTRIBUTE */}
        {imageDataUrls.length > 0 && (
          <div className="image-previews-container"> {/* <--- NEW CONTAINER FOR MULTIPLE PREVIEWS */}
            {imageDataUrls.map((url, index) => (
              <img key={index} src={url} alt={`Preview ${index + 1}`} style={{ maxWidth: '150px', maxHeight: '150px', margin: '5px', border: '1px solid #ccc' }} />
            ))}
          </div>
        )}
        <textarea
          placeholder="Type your question about ALL images here (e.g., 'Solve these math problems', 'Analyze these diagrams')."
          value={imageQuestionText}
          onChange={(e) => setImageQuestionText(e.target.value)}
          rows="3"
          disabled={loading}
        ></textarea>
        <button onClick={handleSubmitImageQuestion} disabled={loading || imageDataUrls.length === 0 || !imageQuestionText}> {/* <--- Adjust disabled condition */}
          {loading ? 'Analyzing Images...' : 'Analyze Image Questions'}
        </button>
      </div>

      {/* MODIFIED: Loop through results for multiple images */}
      {imageAnalysisResults.length > 0 && (
        <div className="all-image-results">
            {imageAnalysisResults.map((analysis, index) => (
                <ImageQuestionDisplay key={index} analysis={analysis} />
            ))}
        </div>
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