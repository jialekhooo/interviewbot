from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.database import Base

# Enum for Difficulty Levels
class DifficultyLevel(PyEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# -------------------
# Interview Session
# -------------------
class DBInterviewSession(Base):
    __tablename__ = 'interview_sessions'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    position = Column(String)
    difficulty = Column(String, default=DifficultyLevel.MEDIUM.value)
    question_types = Column(JSON, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="not_started")

    # Relationships
    questions = relationship("DBInterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    responses = relationship("DBUserResponse", back_populates="session", cascade="all, delete-orphan")
    feedback = relationship("DBInterviewFeedback", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InterviewSession(session_id={self.session_id}, user_id={self.user_id}, status={self.status})>"


# -------------------
# Interview Question
# -------------------
class DBInterviewQuestion(Base):
    __tablename__ = 'interview_questions'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('interview_sessions.session_id'))
    question_id = Column(String, unique=True, index=True)
    question_text = Column(String)

    session = relationship("DBInterviewSession", back_populates="questions")
    responses = relationship("DBUserResponse", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InterviewQuestion(question_text={self.question_text})>"


# -------------------
# User Response
# -------------------
class DBUserResponse(Base):
    __tablename__ = 'user_responses'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('interview_sessions.session_id'))
    question_id = Column(String, ForeignKey('interview_questions.question_id'))
    response_text = Column(String)

    session = relationship("DBInterviewSession", back_populates="responses")
    question = relationship("DBInterviewQuestion", back_populates="responses")

    def __repr__(self):
        return f"<UserResponse(response_text={self.response_text})>"


# -------------------
# Interview Feedback
# -------------------
class DBInterviewFeedback(Base):
    __tablename__ = 'interview_feedbacks'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('interview_sessions.session_id'))
    feedback_text = Column(String)

    session = relationship("DBInterviewSession", back_populates="feedback")

    def __repr__(self):
        return f"<InterviewFeedback(feedback_text={self.feedback_text})>"
