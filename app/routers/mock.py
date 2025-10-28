from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..services.gpt_service import gpt_service
from ..utils.prompt_utils import fill_prompt
import uuid
from datetime import datetime

router = APIRouter()

# Store mock interview sessions
mock_sessions: Dict[str, Dict] = {}

class MockInterviewRequest(BaseModel):
    resume_text: str
    job_description: str = ""
    difficulty: str = "medium"
    question_count: int = 5

class MockQuestion(BaseModel):
    id: str
    question: str
    type: str
    expected_answer: str

class MockInterviewResponse(BaseModel):
    session_id: str
    questions: List[MockQuestion]
    status: str

class MockAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str

class MockAnswerResponse(BaseModel):
    score: float
    feedback: str
    strengths: List[str]
    improvements: List[str]
    next_question: Optional[MockQuestion] = None

@router.post("/start", response_model=MockInterviewResponse)
async def start_mock_interview(request: MockInterviewRequest):
    """
    Start a mock interview session with AI-generated questions
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Generate interview questions using the template
        prompt = fill_prompt(
            "interview_questions",
            resume_json=request.resume_text,
            job_description_text=request.job_description or "General software engineering position"
        )
        
        result = gpt_service.call_gpt(prompt, temperature=0.8)
        
        # If JSON parsing failed but we still have raw_output, continue with fallback
        if "error" in result and "raw_output" not in result:
            raise HTTPException(status_code=500, detail=f"AI service error: {result['error']}")
        
        # Parse questions from response
        questions = []
        if "raw_output" in result:
            # Fallback: create basic questions
            question_texts = [
                "Tell me about yourself and your background",
                "What interests you about this position?",
                "Describe a challenging project you worked on",
                "How do you handle working under pressure?",
                "Where do you see yourself in 5 years?"
            ]
            for i, q_text in enumerate(question_texts[:request.question_count]):
                questions.append(MockQuestion(
                    id=f"q_{i+1}",
                    question=q_text,
                    type="behavioral",
                    expected_answer="Provide specific examples from your experience"
                ))
        else:
            # Parse structured response
            if "questions" in result:
                for i, q in enumerate(result["questions"][:request.question_count]):
                    questions.append(MockQuestion(
                        id=f"q_{i+1}",
                        question=q.get("question", ""),
                        type=q.get("type", "general"),
                        expected_answer=q.get("sample_answer", "")
                    ))
        
        # Store session
        mock_sessions[session_id] = {
            "questions": [q.dict() for q in questions],
            "current_question": 0,
            "answers": [],
            "created_at": datetime.utcnow(),
            "resume_text": request.resume_text,
            "job_description": request.job_description
        }
        
        return MockInterviewResponse(
            session_id=session_id,
            questions=questions,
            status="active"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start mock interview: {str(e)}")

@router.post("/answer", response_model=MockAnswerResponse)
async def submit_mock_answer(request: MockAnswerRequest):
    """
    Submit an answer to a mock interview question and get AI feedback
    """
    try:
        if request.session_id not in mock_sessions:
            raise HTTPException(status_code=404, detail="Mock interview session not found")
        
        session = mock_sessions[request.session_id]
        
        # Find the question
        question_data = None
        for q in session["questions"]:
            if q["id"] == request.question_id:
                question_data = q
                break
        
        if not question_data:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Generate feedback using scoring template
        prompt = fill_prompt(
            "mock_interview_scoring",
            interview_question=question_data["question"],
            user_answer=request.answer
        )
        
        result = gpt_service.call_gpt(prompt, temperature=0.6)
        
        # If JSON parsing failed but raw text exists, proceed with fallback
        if "error" in result and "raw_output" not in result:
            raise HTTPException(status_code=500, detail=f"AI service error: {result['error']}")
        
        # Store the answer
        session["answers"].append({
            "question_id": request.question_id,
            "answer": request.answer,
            "timestamp": datetime.utcnow(),
            "feedback": result
        })
        
        # Determine next question
        current_idx = session["current_question"]
        next_question = None
        if current_idx + 1 < len(session["questions"]):
            session["current_question"] += 1
            next_q_data = session["questions"][current_idx + 1]
            next_question = MockQuestion(**next_q_data)
        
        # Parse feedback
        if "raw_output" in result:
            feedback_text = result["raw_output"]
            return MockAnswerResponse(
                score=0.7,
                feedback=feedback_text,
                strengths=["Good effort"],
                improvements=["See detailed feedback above"],
                next_question=next_question
            )
        
        return MockAnswerResponse(
            score=result.get("score", 0.7),
            feedback=result.get("feedback", "Good answer"),
            strengths=result.get("strengths", []),
            improvements=result.get("improvements", []),
            next_question=next_question
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")

@router.get("/session/{session_id}")
async def get_mock_session(session_id: str):
    """Get mock interview session details"""
    if session_id not in mock_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return mock_sessions[session_id]

@router.get("/health")
async def mock_health():
    """Health check for mock interview service"""
    return {"status": "ok", "service": "mock_interview", "active_sessions": len(mock_sessions)}
