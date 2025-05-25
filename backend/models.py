# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class QuestionAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.String(80), nullable=True) # Optional: if you implement user authentication
    question_text = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    user_answer = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.Text, nullable=True) # Storing correct answer from parsed question
    is_correct = db.Column(db.Boolean, nullable=False)
    time_taken_seconds = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<QuestionAttempt {self.id} - {self.topic} - {self.is_correct}>'

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'question_text': self.question_text,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'user_answer': self.user_answer,
            'correct_answer': self.correct_answer,
            'is_correct': self.is_correct,
            'time_taken_seconds': self.time_taken_seconds
        }