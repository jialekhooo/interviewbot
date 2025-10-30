from pydantic import BaseModel
from typing import Optional


class ResumeBuilderRequest(BaseModel):
    """Schema for resume builder request"""
    name: str
    course: str  # What's your course?
    education_background: str  # Education background
    skills: str  # Skills you have
    internship_experience: str  # Internship Experience
    additional_info: Optional[str] = ""  # Anything you want to add?
    user_id: Optional[str] = None


class ResumeBuilderResponse(BaseModel):
    """Schema for resume builder response"""
    success: bool
    resume_text: str
    resume_html: Optional[str] = None
    suggestions: Optional[list] = None
    
    class Config:
        from_attributes = True
