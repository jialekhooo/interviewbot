from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import date
from enum import Enum

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    DOCTORATE = "doctorate"
    PROFESSIONAL = "professional"
    OTHER = "other"

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: date
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    description: Optional[str] = None
    level: Optional[EducationLevel] = None

class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    current: bool = False
    description: str
    skills: List[str] = []
    level: Optional[ExperienceLevel] = None

class Project(BaseModel):
    name: str
    description: str
    start_date: date
    end_date: Optional[date] = None
    current: bool = False
    url: Optional[HttpUrl] = None
    technologies: List[str] = []

class Skill(BaseModel):
    name: str
    proficiency: Optional[float] = Field(None, ge=0, le=1)  # 0 to 1 scale
    years_of_experience: Optional[float] = None
    category: Optional[str] = None  # e.g., "Programming", "Framework", "Tool"

class Resume(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    summary: Optional[str] = None
    education: List[Education] = []
    experience: List[Experience] = []
    projects: List[Project] = []
    skills: List[Skill] = []
    certifications: List[Dict[str, str]] = []
    languages: List[Dict[str, str]] = []
    awards: List[Dict[str, str]] = []

class ResumeAnalysisResponse(BaseModel):
    file_id: str
    file_name: str
    uploaded_at: str
    analysis: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "550e8400-e29b-41d4-a716-446655440000",
                "file_name": "john_doe_resume.pdf",
                "uploaded_at": "2023-01-01T12:00:00Z",
                "analysis": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "summary": "Experienced software engineer with 5+ years of experience...",
                    "skills": ["Python", "JavaScript", "React", "Node.js"],
                    "experience_years": 5,
                    "education_level": "bachelors",
                    "score": 85,
                    "strengths": ["Strong technical skills", "Relevant experience"],
                    "improvements": ["Could include more metrics", "Add more details about projects"]
                }
            }
        }