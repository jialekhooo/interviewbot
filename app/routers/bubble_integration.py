from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..services.gpt_service import gpt_service
from ..utils.prompt_utils import fill_prompt
import uuid
from datetime import datetime

router = APIRouter()

# Bubble.io friendly models with simple field names
class BubbleInterviewStart(BaseModel):
    position: str = "Software Engineer"
    difficulty: str = "medium"
    question_types: List[str] = ["behavioral", "technical"]
    duration: int = 30

class BubbleInterviewAnswer(BaseModel):
    session_id: str
    response: str
    time_taken: Optional[int] = None

class BubbleResumeAnalysis(BaseModel):
    resume_text: str
    target_role: str = ""

class BubbleGuidance(BaseModel):
    question: str
    user_answer: str
    context: str = ""

# Simple response models for Bubble.io
class SimpleResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] = {}

@router.post("/interview/start", response_model=SimpleResponse)
async def bubble_start_interview(request: BubbleInterviewStart):
    """
    Bubble.io friendly interview start endpoint
    Returns simple success/failure with data
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Generate first question using AI
        prompt = f"""You are a professional interviewer for a {request.position} position.
        Generate 1 {request.difficulty} difficulty {request.question_types[0]} interview question.
        Return only the question text, no additional formatting."""
        
        result = gpt_service.call_gpt(prompt, temperature=0.7)
        
        if "error" in result:
            return SimpleResponse(
                success=False,
                message=f"AI service error: {result['error']}",
                data={}
            )
        
        question_text = result.get("raw_output", "Tell me about yourself and your background.")
        
        return SimpleResponse(
            success=True,
            message="Interview started successfully",
            data={
                "session_id": session_id,
                "question": question_text,
                "status": "active",
                "position": request.position,
                "difficulty": request.difficulty
            }
        )
        
    except Exception as e:
        return SimpleResponse(
            success=False,
            message=f"Failed to start interview: {str(e)}",
            data={}
        )

@router.post("/interview/answer", response_model=SimpleResponse)
async def bubble_submit_answer(request: BubbleInterviewAnswer):
    """
    Bubble.io friendly answer submission
    """
    try:
        # Generate feedback using AI
        prompt = f"""You are an interview coach. A candidate answered: "{request.response}"
        
        Provide brief feedback in this format:
        FEEDBACK: [2-3 sentences of constructive feedback]
        SCORE: [number from 1-10]
        NEXT_QUESTION: [a follow-up interview question]"""
        
        result = gpt_service.call_gpt(prompt, temperature=0.6)
        
        if "error" in result:
            return SimpleResponse(
                success=False,
                message=f"AI service error: {result['error']}",
                data={}
            )
        
        feedback_text = result.get("raw_output", "Good answer! Keep practicing.")
        
        # Parse the response
        lines = feedback_text.split('\n')
        feedback = ""
        score = 7
        next_question = "What are your career goals?"
        
        for line in lines:
            if line.startswith("FEEDBACK:"):
                feedback = line.replace("FEEDBACK:", "").strip()
            elif line.startswith("SCORE:"):
                try:
                    score = int(line.replace("SCORE:", "").strip())
                except:
                    score = 7
            elif line.startswith("NEXT_QUESTION:"):
                next_question = line.replace("NEXT_QUESTION:", "").strip()
        
        return SimpleResponse(
            success=True,
            message="Answer processed successfully",
            data={
                "feedback": feedback or feedback_text,
                "score": score,
                "next_question": next_question,
                "session_id": request.session_id
            }
        )
        
    except Exception as e:
        return SimpleResponse(
            success=False,
            message=f"Failed to process answer: {str(e)}",
            data={}
        )

@router.post("/resume/analyze", response_model=SimpleResponse)
async def bubble_analyze_resume(request: BubbleResumeAnalysis):
    """
    Bubble.io friendly resume analysis
    """
    try:
        prompt = fill_prompt(
            "resume_improvement",
            resume_text=request.resume_text,
            target_role=request.target_role or "software engineering position",
            experience_level="mid"
        )
        
        result = gpt_service.call_gpt(prompt, temperature=0.6)
        
        if "error" in result:
            return SimpleResponse(
                success=False,
                message=f"AI service error: {result['error']}",
                data={}
            )
        
        analysis = result.get("raw_output", "Resume looks good overall.")
        
        return SimpleResponse(
            success=True,
            message="Resume analyzed successfully",
            data={
                "analysis": analysis,
                "score": 7.5,
                "target_role": request.target_role
            }
        )
        
    except Exception as e:
        return SimpleResponse(
            success=False,
            message=f"Failed to analyze resume: {str(e)}",
            data={}
        )

@router.post("/guidance/improve", response_model=SimpleResponse)
async def bubble_get_guidance(request: BubbleGuidance):
    """
    Bubble.io friendly answer guidance
    """
    try:
        prompt = fill_prompt(
            "answer_guidance",
            question=request.question,
            user_answer=request.user_answer,
            context=request.context
        )
        
        result = gpt_service.call_gpt(prompt, temperature=0.7)
        
        if "error" in result:
            return SimpleResponse(
                success=False,
                message=f"AI service error: {result['error']}",
                data={}
            )
        
        guidance = result.get("raw_output", "Good effort! Keep practicing.")
        
        return SimpleResponse(
            success=True,
            message="Guidance generated successfully",
            data={
                "guidance": guidance,
                "question": request.question,
                "improved_answer": "See guidance for specific improvements"
            }
        )
        
    except Exception as e:
        return SimpleResponse(
            success=False,
            message=f"Failed to generate guidance: {str(e)}",
            data={}
        )

@router.get("/health")
async def bubble_health():
    """Health check for Bubble.io integration"""
    return SimpleResponse(
        success=True,
        message="Bubble.io integration is healthy",
        data={
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": [
                "/api/bubble/interview/start",
                "/api/bubble/interview/answer", 
                "/api/bubble/resume/analyze",
                "/api/bubble/guidance/improve"
            ]
        }
    )
