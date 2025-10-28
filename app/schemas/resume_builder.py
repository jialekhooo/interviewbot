from pydantic import BaseModel
from typing import Optional


class ResumeBuilderRequest(BaseModel):
    """Schema for resume builder request"""
    name: str
    major: str
    education_background: str
    skills: str
    internship_experience: str
    additional_info: Optional[str] = ""
    user_id: Optional[str] = None


class ResumeBuilderResponse(BaseModel):
    """Schema for resume builder response"""
    success: bool
    resume_text: str
    resume_html: Optional[str] = None
    suggestions: Optional[list] = None
    
    class Config:
        from_attributes = True
