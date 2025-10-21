from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from app.services.gpt_service import gpt_service
import json

router = APIRouter()

# Store active live sessions
live_sessions: Dict[str, Dict[str, Any]] = {}

class LiveInterviewStart(BaseModel):
    position: str = "Software Engineer"
    difficulty: str = "medium"
    duration: int = 30

class AnswerWithEmotions(BaseModel):
    session_id: str
    transcript: str
    emotion: str
    confidence: float
    face_detected: bool

class LiveFeedback(BaseModel):
    score: float
    feedback: str
    strengths: List[str]
    improvements: List[str]

@router.post("/start")
async def start_live_interview(request: LiveInterviewStart):
    """
    Start a live interview session with computer vision and speech-to-text.
    No file uploads needed.
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Generate first question
        system_prompt = f"You are a virtual interviewer for a {request.position} role."
        user_prompt = f"Generate a {request.difficulty} level interview question for opening."
        
        result = gpt_service.call_gpt_with_system(system_prompt, user_prompt)
        question_text = result.get("raw_output", "Tell me about yourself and your background.")
        
        # Store session
        live_sessions[session_id] = {
            "position": request.position,
            "difficulty": request.difficulty,
            "created_at": datetime.utcnow(),
            "questions_asked": 1,
            "responses": [],
            "current_question": question_text,
            "status": "active"
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "question": question_text,
            "position": request.position,
            "difficulty": request.difficulty
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start live interview: {str(e)}")

@router.post("/submit-answer")
async def submit_live_answer(request: AnswerWithEmotions):
    """
    Submit an answer with real-time computer vision and speech data.
    No file upload required.
    """
    try:
        if request.session_id not in live_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = live_sessions[request.session_id]
        
        # Store the response with emotion data
        response_data = {
            "transcript": request.transcript,
            "emotion": request.emotion,
            "confidence": request.confidence,
            "face_detected": request.face_detected,
            "timestamp": datetime.utcnow()
        }
        session["responses"].append(response_data)
        
        # Generate AI feedback using GPT
        system_prompt = "You are an expert interview coach providing real-time feedback."
        feedback_prompt = f"""
        The candidate answered this question:
        "{session['current_question']}"
        
        With this response:
        "{request.transcript}"
        
        They appeared: {request.emotion} (confidence: {request.confidence}%)
        Face was detected: {request.face_detected}
        
        Provide structured feedback in JSON format:
        {{
            "score": 0.0-1.0,
            "feedback": "Brief overall feedback",
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"],
            "next_question": "Next interview question"
        }}
        """
        
        feedback_result = gpt_service.call_gpt_with_system(system_prompt, feedback_prompt)
        
        # Parse feedback
        try:
            if isinstance(feedback_result, dict) and "raw_output" in feedback_result:
                # Extract JSON from raw output
                feedback_json = json.loads(feedback_result["raw_output"])
            else:
                feedback_json = feedback_result
        except:
            feedback_json = {
                "score": 0.7,
                "feedback": "Good response. Keep practicing to improve further.",
                "strengths": ["Communication"],
                "improvements": ["Add specific examples"],
                "next_question": "Tell me about your biggest achievement."
            }
        
        # Update session with next question
        next_question = feedback_json.get("next_question", "Tell me about your career goals.")
        session["current_question"] = next_question
        session["questions_asked"] += 1
        
        # Check if interview should continue
        max_questions = 5
        interview_complete = session["questions_asked"] >= max_questions
        
        if interview_complete:
            session["status"] = "completed"
        
        return {
            "success": True,
            "feedback": {
                "score": feedback_json.get("score", 0.7),
                "feedback": feedback_json.get("feedback", "Good response"),
                "strengths": feedback_json.get("strengths", []),
                "improvements": feedback_json.get("improvements", [])
            },
            "next_question": next_question,
            "interview_complete": interview_complete,
            "questions_answered": session["questions_asked"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")

@router.post("/end-session")
async def end_live_session(session_id: str):
    """
    End a live interview session and get final summary.
    """
    try:
        if session_id not in live_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = live_sessions[session_id]
        session["status"] = "completed"
        session["ended_at"] = datetime.utcnow()
        
        # Calculate summary statistics
        emotions = [r["emotion"] for r in session["responses"]]
        avg_confidence = sum(r["confidence"] for r in session["responses"]) / len(session["responses"]) if session["responses"] else 0
        
        return {
            "success": True,
            "summary": {
                "total_questions": session["questions_asked"],
                "total_responses": len(session["responses"]),
                "average_emotion_confidence": avg_confidence,
                "emotions_detected": list(set(emotions)),
                "position": session["position"],
                "difficulty": session["difficulty"],
                "duration": (session["ended_at"] - session["created_at"]).total_seconds() / 60
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@router.get("/session/{session_id}")
async def get_live_session(session_id: str):
    """
    Get details about a live interview session.
    """
    if session_id not in live_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = live_sessions[session_id]
    return {
        "session_id": session_id,
        "position": session["position"],
        "difficulty": session["difficulty"],
        "status": session["status"],
        "questions_asked": session["questions_asked"],
        "current_question": session["current_question"],
        "responses_count": len(session["responses"])
    }

@router.get("/health")
async def live_interview_health():
    """Health check for live interview service"""
    return {
        "status": "ok",
        "service": "live_interview",
        "active_sessions": len([s for s in live_sessions.values() if s["status"] == "active"])
    }
