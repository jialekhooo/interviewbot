from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi import Request
from typing import List, Dict, Optional
import json
import uuid
from datetime import datetime
from ..services.interview_simulator import InterviewSimulator
from ..schemas.interview import InterviewSession, InterviewFeedback, InterviewQuestion
from pydantic import BaseModel, Field
router = APIRouter()

# Store active interview sessions
active_sessions: Dict[str, InterviewSession] = {}

@router.get("/health")
async def interview_health():
    """Health check for interview service"""
    return {"status": "ok", "service": "interview", "active_sessions": len(active_sessions)}

@router.post("/start")
async def start_interview(request: Request):
    """
    Start a new interview session
    """
    # Parse JSON body with defaults
    body: Dict = {}
    try:
        body = await request.json()
    except Exception:
        # If JSON parsing fails, try form data
        try:
            form = await request.form()
            body = dict(form)
            # Handle repeated fields like question_types[]
            if "question_types[]" in form:
                body["question_types"] = form.getlist("question_types[]")
        except Exception:
            # If both fail, use empty dict (will use defaults below)
            body = {}

    position = body.get("position", "Software Engineer")
    difficulty = body.get("difficulty", "medium")
    q_types = body.get("question_types", ["behavioral", "technical"])
    # Normalize question_types to list[str]
    if isinstance(q_types, str):
        q_types = [s.strip() for s in q_types.split(",") if s.strip()]
    elif not isinstance(q_types, list):
        # Try to coerce to list if a single value came through
        q_types = [str(q_types)] if q_types is not None else ["behavioral", "technical"]
    duration = body.get("duration", 30)

    session_id = str(uuid.uuid4())
    # Use a lightweight dict for session storage to avoid schema strictness here
    session = {
        "session_id": session_id,
        "position": position,
        "difficulty": difficulty,
        "question_types": q_types,
        "duration": duration,
        "start_time": datetime.utcnow(),
        "status": "in_progress",
        "questions": [],
        "feedback": []
    }
    
    # Initialize the interview simulator
    simulator = InterviewSimulator(
        position=position,
        difficulty=difficulty,
        question_types=q_types,
    )
    
    # Generate first question
    first_question = simulator.generate_question()
    session["questions"].append(first_question)
    
    # Store the session
    active_sessions[session_id] = session
    
    return {
        "session_id": session_id,
        "question": first_question,
        "status": session["status"]
    }

class AnswerPayload(BaseModel):
    session_id: str = Field(..., example="uuid")
    response: str = Field(..., example="<your answer text>")
    time_taken: int = Field(..., example=60)
    confidence_level: float = Field(..., example=0.8)

# --- Active sessions dict (mock) ---
active_sessions = {}

# --- Mock InterviewSimulator class ---
class InterviewSimulator:
    def __init__(self, position, difficulty, question_types):
        self.position = position
        self.difficulty = difficulty
        self.question_types = question_types

    def analyze_response(self, question, user_response, time_taken, confidence_level):
        return {"analysis": f"Feedback for {user_response}"}

    def generate_question(self):
        return "Next interview question?"

    def generate_overall_feedback(self):
        return {"summary": "Overall performance feedback."}

@router.post("/answer")
async def submit_answer(payload: AnswerPayload):
    """
    Submit an answer to the current question and receive AI feedback.
    Returns feedback and the next question if the interview continues.
    """
    session_id = payload.session_id
    if not session_id or session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    if not session.get("questions"):
        raise HTTPException(status_code=400, detail="No question found in session")

    # Recreate simulator
    simulator = InterviewSimulator(
        position=session["position"],
        difficulty=session["difficulty"],
        question_types=session["question_types"],
    )

    last_question = session["questions"][-1]
    feedback = simulator.analyze_response(
        question=last_question,
        user_response=payload.response,
        time_taken=payload.time_taken,
        confidence_level=payload.confidence_level,
    )

    session["feedback"].append(feedback)

    # Generate next question or end interview
    if len(session["questions"]) < 5:
        next_question = simulator.generate_question()
        session["questions"].append(next_question)
        return {
            "type": "next_question",
            "feedback": feedback,
            "question": next_question,
            "session_id": session_id,
        }
    else:
        session["status"] = "completed"
        session["end_time"] = datetime.utcnow()
        overall = simulator.generate_overall_feedback()
        return {
            "type": "interview_complete",
            "feedback": overall,
            "session_summary": {
                "total_questions": len(session["questions"]),
                "duration": (session["end_time"] - session["start_time"]).total_seconds() / 60,
            },
            "session_id": session_id,
        }

@router.websocket("/ws/{session_id}")
async def websocket_interview(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time interview simulation
    """
    if session_id not in active_sessions:
        await websocket.close(code=4000)
        return
    
    session = active_sessions[session_id]
    simulator = InterviewSimulator(
        position=session.position,
        difficulty=session.difficulty,
        question_types=session.question_types
    )
    
    await websocket.accept()
    
    try:
        while True:
            # Receive user's response to the current question
            data = await websocket.receive_text()
            user_response = json.loads(data)
            
            # Analyze the response and generate feedback
            feedback = simulator.analyze_response(
                question=session.questions[-1],
                user_response=user_response.get("response", "")
            )
            
            # Store the feedback
            if not session.feedback:
                session.feedback = []
            session.feedback.append(feedback)
            
            # Generate next question or end interview
            if len(session.questions) < 5:  # Example: 5 questions per session
                next_question = simulator.generate_question()
                session.questions.append(next_question)
                await websocket.send_json({
                    "type": "next_question",
                    "question": next_question.dict(),
                    "feedback": feedback.dict()
                })
            else:
                # End of interview
                session.status = "completed"
                session.end_time = datetime.utcnow()
                
                # Generate overall feedback
                overall_feedback = simulator.generate_overall_feedback(session)
                
                await websocket.send_json({
                    "type": "interview_complete",
                    "feedback": overall_feedback.dict(),
                    "session_summary": {
                        "total_questions": len(session.questions),
                        "duration": (session.end_time - session.start_time).total_seconds() / 60
                    }
                })
                break
                
    except WebSocketDisconnect:
        # Handle client disconnection
        if session.status == "in_progress":
            session.status = "abandoned"
            session.end_time = datetime.utcnow()
    
    finally:
        # Clean up
        if session_id in active_sessions:
            del active_sessions[session_id]

@router.get("/feedback/{session_id}")
async def get_interview_feedback(session_id: str):
    """
    Get feedback for a completed interview session
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Interview not completed yet")
    
    return {
        "session_id": session_id,
        "feedback": session.feedback,
        "questions": [q.dict() for q in session.questions],
        "start_time": session.start_time,
        "end_time": session.end_time,
        "duration": (session.end_time - session.start_time).total_seconds() / 60
    }
