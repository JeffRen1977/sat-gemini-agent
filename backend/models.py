# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class QuestionAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.String(80), nullable=True) # Optional: if you implement user authentication

    # Fields for text-based questions
    question_text = db.Column(db.Text, nullable=True) # Changed to nullable=True
    topic = db.Column(db.String(100), nullable=True) # Changed to nullable=True
    difficulty = db.Column(db.String(50), nullable=True) # Changed to nullable=True
    user_answer = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.Text, nullable=True) # Storing correct answer from parsed question
    is_correct = db.Column(db.Boolean, nullable=True) # Changed to nullable=True
    time_taken_seconds = db.Column(db.Integer, nullable=True)

    # NEW FIELDS FOR IMAGE-BASED QUESTIONS
    is_image_question = db.Column(db.Boolean, default=False, nullable=False)
    image_base64_preview = db.Column(db.Text, nullable=True) # Store a small preview or path if large
    user_image_prompt = db.Column(db.Text, nullable=True) # The text question user asks about the image
    ai_generated_solution = db.Column(db.Text, nullable=True) # Gemini's full solution/explanation for image Q
    ai_generated_answer = db.Column(db.String(255), nullable=True) # A short answer from Gemini (if applicable)

    def __repr__(self):
        return f'<QuestionAttempt {self.id} - {"Image" if self.is_image_question else self.topic}>'

    def to_dict(self):
        data = {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'is_image_question': self.is_image_question,
            'image_base64_preview': self.image_base64_preview,
            'user_image_prompt': self.user_image_prompt,
            'ai_generated_solution': self.ai_generated_solution,
            'ai_generated_answer': self.ai_generated_answer
        }
        if not self.is_image_question:
            data.update({
                'question_text': self.question_text,
                'topic': self.topic,
                'difficulty': self.difficulty,
                'user_answer': self.user_answer,
                'correct_answer': self.correct_answer,
                'is_correct': self.is_correct,
                'time_taken_seconds': self.time_taken_seconds
            })
        return data