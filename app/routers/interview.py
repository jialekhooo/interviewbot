from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict, Optional
import json
import uuid
from datetime import datetime
from ..services.interview_simulator import InterviewSimulator
from ..schemas.interview import InterviewSession, InterviewFeedback, InterviewQuestion

router = APIRouter()

# Store active interview sessions
active_sessions: Dict[str, InterviewSession] = {}

@router.post("/start")
async def start_interview(
    position: str,
    difficulty: str = "medium",
    question_types: List[str] = ["behavioral", "technical"],
    duration: int = 30
):
    """
    Start a new interview session
    """
    session_id = str(uuid.uuid4())
    session = InterviewSession(
        session_id=session_id,
        position=position,
        difficulty=difficulty,
        question_types=question_types,
        duration=duration,
        start_time=datetime.utcnow(),
        status="in_progress",
        questions=[],
        feedback=None
    )
    
    # Initialize the interview simulator
    simulator = InterviewSimulator(
        position=position,
        difficulty=difficulty,
        question_types=question_types
    )
    
    # Generate first question
    first_question = simulator.generate_question()
    session.questions.append(first_question)
    
    # Store the session
    active_sessions[session_id] = session
    
    return {
        "session_id": session_id,
        "question": first_question.dict(),
        "status": session.status
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
