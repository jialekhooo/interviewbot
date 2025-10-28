from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class DBVideoInterview(Base):
    """Model for storing video interview sessions"""
    __tablename__ = 'video_interviews'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    position = Column(String)
    question_text = Column(Text)
    video_path = Column(String, nullable=True)  # Path to stored video file
    video_duration = Column(Integer, nullable=True)  # Duration in seconds
    transcript = Column(Text, nullable=True)  # Speech-to-text transcript
    analysis = Column(JSON, nullable=True)  # AI analysis results
    feedback = Column(Text, nullable=True)  # Overall feedback
    scores = Column(JSON, nullable=True)  # Scoring breakdown
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, processing, completed, failed

    def __repr__(self):
        return f"<VideoInterview(session_id={self.session_id}, user_id={self.user_id}, status={self.status})>"
