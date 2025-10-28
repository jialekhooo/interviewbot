from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class VideoInterviewCreate(BaseModel):
    """Schema for creating a new video interview session"""
    user_id: str
    position: str
    question_text: str


class VideoInterviewUpload(BaseModel):
    """Schema for uploading video data"""
    session_id: str


class VideoInterviewResponse(BaseModel):
    """Schema for video interview response"""
    session_id: str
    user_id: str
    position: str
    question_text: str
    video_path: Optional[str] = None
    video_duration: Optional[int] = None
    transcript: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    scores: Optional[Dict[str, Any]] = None
    created_at: datetime
    status: str

    class Config:
        from_attributes = True


class VideoAnalysisResult(BaseModel):
    """Schema for video analysis results"""
    transcript: str
    feedback: str
    scores: Dict[str, Any]
    analysis: Dict[str, Any]
