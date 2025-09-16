from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    ALGORITHM = "algorithm"
    CULTURE_FIT = "culture_fit"
    CASE_STUDY = "case_study"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class InterviewQuestion(BaseModel):
    question_id: str
    text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    category: Optional[str] = None
    time_limit: Optional[int] = Field(
        default=180,  # Default 3 minutes
        description="Time limit in seconds"
    )
    sample_answer: Optional[str] = None
    evaluation_criteria: List[str] = []
    keywords: List[str] = []
    follow_up_questions: List[str] = []

class UserResponse(BaseModel):
    question_id: str
    response_text: str
    time_taken: float  # in seconds
    confidence_level: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="User's self-assessed confidence level (0-1)"
    )

class FeedbackCategory(str, Enum):
    CONTENT = "content"
    CLARITY = "clarity"
    STRUCTURE = "structure"
    TECHNICAL_ACCURACY = "technical_accuracy"
    COMMUNICATION = "communication"
    TIME_MANAGEMENT = "time_management"

class FeedbackItem(BaseModel):
    category: FeedbackCategory
    score: float = Field(ge=0, le=1)  # 0 to 1 scale
    comments: str
    suggestions: List[str] = []
    strengths: List[str] = []
    areas_for_improvement: List[str] = []

class InterviewFeedback(BaseModel):
    question_id: str
    user_response: str
    feedback_items: List[FeedbackItem]
    overall_score: float = Field(ge=0, le=1)
    summary: str
    suggested_responses: List[str] = []
    follow_up_questions: List[str] = []

class InterviewSession(BaseModel):
    session_id: str
    user_id: str
    position: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    question_types: List[QuestionType] = [QuestionType.BEHAVIORAL, QuestionType.TECHNICAL]
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "not_started"  # not_started, in_progress, completed, abandoned
    questions: List[InterviewQuestion] = []
    responses: List[UserResponse] = []
    feedback: Optional[List[InterviewFeedback]] = None
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

class InterviewResult(BaseModel):
    session_id: str
    user_id: str
    position: str
    start_time: datetime
    end_time: datetime
    total_questions: int
    average_score: float
    feedback_summary: str
    strengths: List[str]
    areas_for_improvement: List[str]
    detailed_feedback: List[Dict[str, Any]]
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user123",
                "position": "Senior Software Engineer",
                "start_time": "2023-01-01T10:00:00Z",
                "end_time": "2023-01-01T10:45:30Z",
                "total_questions": 5,
                "average_score": 0.78,
                "feedback_summary": "You demonstrated strong technical knowledge but could improve your communication and time management.",
                "strengths": [
                    "Solid understanding of data structures",
                    "Good problem-solving approach"
                ],
                "areas_for_improvement": [
                    "Speak more clearly and concisely",
                    "Spend less time on the first question"
                ],
                "detailed_feedback": [
                    {
                        "question": "Tell me about a time you faced a difficult technical challenge and how you overcame it.",
                        "score": 0.85,
                        "feedback": "Great example with clear explanation of the problem and solution."
                    },
                    {
                        "question": "Design a URL shortening service like bit.ly.",
                        "score": 0.7,
                        "feedback": "Good start but could have covered more edge cases and scalability aspects."
                    }
                ]
            }
        }
