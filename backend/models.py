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


# New Models for Mock Tests
class MockTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_duration_minutes = db.Column(db.Integer, nullable=False) # Overall estimated duration
    sections = db.relationship('MockTestSection', backref='mock_test', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'total_duration_minutes': self.total_duration_minutes,
            'sections': [section.to_dict() for section in self.sections]
        }

class MockTestSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_test.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False) # To define the sequence of sections
    duration_minutes = db.Column(db.Integer, nullable=False)
    # Stores JSON string, e.g., {"topic": "algebra", "difficulty": "medium", "count": 5, "type": "multiple_choice"}
    question_generation_config = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'mock_test_id': self.mock_test_id,
            'title': self.title,
            'order': self.order,
            'duration_minutes': self.duration_minutes,
            'question_generation_config': json.loads(self.question_generation_config) if self.question_generation_config else {}
        }

class UserMockTestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_test.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='started', nullable=False) # E.g., 'started', 'in-progress', 'completed'
    # Stores JSON string, e.g., {"section_1_score": 80, "section_2_score": 75}
    score_details = db.Column(db.Text, nullable=True)
    # Relationship to actual questions attempted, if needed for detailed review
    # question_attempts = db.relationship('MockTestQuestionAttempt', backref='user_mock_test_attempt', lazy=True)


    # Relationships to retrieve parent objects easily
    user = db.relationship('User', backref='mock_test_attempts')
    mock_test = db.relationship('MockTest', backref='user_attempts')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mock_test_id': self.mock_test_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'score_details': json.loads(self.score_details) if self.score_details else {}
        }

# Association table for Word and WordList (many-to-many)
word_to_word_list = db.Table('word_to_word_list',
    db.Column('word_id', db.Integer, db.ForeignKey('word.id'), primary_key=True),
    db.Column('word_list_id', db.Integer, db.ForeignKey('word_list.id'), primary_key=True)
)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), unique=True, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    example_sentence = db.Column(db.Text, nullable=True)
    difficulty_level = db.Column(db.String(50), nullable=True) # e.g., easy, medium, hard (could be 1-5)
    # Relationship to WordList (many-to-many)
    word_lists = db.relationship('WordList', secondary=word_to_word_list, back_populates='words')
    # Relationship to UserWordProgress
    user_progress = db.relationship('UserWordProgress', backref='word', lazy='dynamic')


    def to_dict(self):
        return {
            'id': self.id,
            'term': self.term,
            'definition': self.definition,
            'example_sentence': self.example_sentence,
            'difficulty_level': self.difficulty_level,
            'word_list_ids': [wl.id for wl in self.word_lists]
        }

class WordList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    # Relationship to Word (many-to-many)
    words = db.relationship('Word', secondary=word_to_word_list, back_populates='word_lists')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'word_count': len(self.words)
        }

class UserWordProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='new') # e.g., new, learning, mastered, needs_review
    last_reviewed_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    review_count = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)

    # Unique constraint for user_id and word_id
    __table_args__ = (db.UniqueConstraint('user_id', 'word_id', name='_user_word_uc'),)

    # Relationships
    user = db.relationship('User', backref=db.backref('word_progress_items', lazy='dynamic'))
    # word relationship is defined in Word model via backref='word'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word_id': self.word_id,
            'term': self.word.term if self.word else None, # Include term for convenience
            'status': self.status,
            'last_reviewed_at': self.last_reviewed_at.isoformat(),
            'review_count': self.review_count,
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count
        }

# Models for Essay Writing Assistant
class EssayTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False) # This could be the essay prompt or a passage
    category = db.Column(db.String(100), nullable=True) # e.g., Analytical, Argumentative, Expository
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship('UserEssaySubmission', backref='topic', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }

class UserEssaySubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    essay_topic_id = db.Column(db.Integer, db.ForeignKey('essay_topic.id'), nullable=True) # Nullable if user submits an essay not tied to a predefined topic

    essay_title = db.Column(db.String(250), nullable=True) # User-defined title, or topic title
    essay_text = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)

    feedback_json = db.Column(db.Text, nullable=True) # Stores the detailed JSON feedback from Gemini
    score_summary = db.Column(db.String(250), nullable=True) # E.g., "Overall: 4/6, Strengths: Clarity"

    user = db.relationship('User', backref=db.backref('essay_submissions', lazy='dynamic'))
    # 'topic' backref is defined in EssayTopic model

    def to_dict(self, include_full_text=False, include_full_feedback=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'essay_topic_id': self.essay_topic_id,
            'essay_topic_title': self.topic.title if self.topic else "Custom Topic",
            'essay_title': self.essay_title or (self.topic.title if self.topic else "Untitled Essay"),
            'submission_date': self.submission_date.isoformat(),
            'score_summary': self.score_summary
        }
        if include_full_text:
            data['essay_text'] = self.essay_text
        if include_full_feedback:
            data['feedback_json'] = json.loads(self.feedback_json) if self.feedback_json else None
        return data