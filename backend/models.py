# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

# NEW MODEL: User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False) # Example: can be email or a unique ID
    # Add a relationship to QuestionAttempt if you want to easily query attempts by user
    attempts = db.relationship('QuestionAttempt', backref='user', lazy=True)

    # NEW FIELDS FOR USER PROFILE
    learning_goals = db.Column(db.Text, nullable=True) # Stores JSON string, e.g., '["master Python data analysis", "achieve SAT math score 700"]'
    learning_style_preference = db.Column(db.String(50), nullable=True) # E.g., "visual", "auditory", "kinesthetic", "reading/writing"
    current_knowledge_level = db.Column(db.Text, nullable=True) # Stores JSON string, e.g., '{"math": "intermediate", "reading": "beginner"}'
    preferences = db.Column(db.Text, nullable=True) # Stores JSON string, e.g., '{"explanation_detail": "high", "exercise_type": "interactive"}'

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        # Safely load JSON fields, defaulting to empty dict/list if None or invalid
        return {
            'id': self.id,
            'username': self.username,
            'learning_goals': json.loads(self.learning_goals) if self.learning_goals else [],
            'learning_style_preference': self.learning_style_preference,
            'current_knowledge_level': json.loads(self.current_knowledge_level) if self.current_knowledge_level else {},
            'preferences': json.loads(self.preferences) if self.preferences else {}
        }


class QuestionAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # MODIFIED: Link to the new User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Foreign key to the User table

    # Fields for text-based questions
    question_text = db.Column(db.Text, nullable=True)
    topic = db.Column(db.String(100), nullable=True)
    difficulty = db.Column(db.String(50), nullable=True)
    user_answer = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=True)
    time_taken_seconds = db.Column(db.Integer, nullable=True)

    # NEW FIELDS FOR IMAGE-BASED QUESTIONS
    is_image_question = db.Column(db.Boolean, default=False, nullable=False)
    image_base64_preview = db.Column(db.Text, nullable=True)
    user_image_prompt = db.Column(db.Text, nullable=True)
    ai_generated_solution = db.Column(db.Text, nullable=True)
    ai_generated_answer = db.Column(db.String(255), nullable=True)

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
            'ai_generated_answer': self.ai_generated_answer,
            'ai_generated_solution': json.loads(self.ai_generated_solution) if self.ai_generated_solution and self.is_image_question else self.ai_generated_solution
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