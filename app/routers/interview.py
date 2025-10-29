from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Form, UploadFile, File
from fastapi import Request
from typing import List, Dict
import json
import logging
import uuid
from datetime import datetime
from app.services.interview_simulator import InterviewSimulator
from app.schemas.interview import InterviewSession, InterviewQuestion, UserResponse, StartInterviewSession
from app.models.interview import DBInterviewSession, DBInterviewQuestion, DBUserResponse, DBInterviewFeedback
from app.schemas.auth import User
from app.routers.auth import get_current_active_user
from typing import Optional
from app.database import get_db
from sqlalchemy.orm import Session
from app.services.gpt_service import gpt_service
from fastapi import status
router = APIRouter()

# Store active interview sessions
active_sessions: Dict[str, InterviewSession] = {}

@router.get("/health")
async def interview_health():
    """Health check for interview service"""
    return {"status": "ok", "service": "interview", "active_sessions": len(active_sessions)}

@router.get("/past_interviews", response_model=List[InterviewSession])
async def get_past_interviews(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """
    Retrieve all past interview sessions for a specific user.
    Fetch only the required columns and exclude unnecessary data.
    """
    # Select only the required columns from the InterviewSession table
    past_interviews = db.query(
        DBInterviewSession.session_id,
        DBInterviewSession.user_id,
        DBInterviewSession.position,
        DBInterviewSession.difficulty,
        DBInterviewSession.question_types,
        DBInterviewSession.start_time,
        DBInterviewSession.end_time,
        DBInterviewSession.status
    ).filter(
        DBInterviewSession.user_id == current_user.username
    ).all()

    if not past_interviews:
        raise HTTPException(status_code=404, detail="No past interviews found for this user")

    # Return the result directly as the response model will handle serialization
    return past_interviews

@router.get("/past_interview/{session_id}")
async def get_past_interview(session_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """
    Retrieve a specific past interview session with all its questions, responses, and feedback.
    """
    # Fetch the interview session and verify it belongs to the current user
    past_interview = db.query(DBInterviewSession).filter(
        DBInterviewSession.session_id == session_id,
        DBInterviewSession.user_id == current_user.username
    ).first()
    
    if not past_interview:
        raise HTTPException(status_code=404, detail="Interview session not found or access denied")
    
    # Fetch related data for questions, responses, and feedback
    questions = db.query(DBInterviewQuestion).filter(DBInterviewQuestion.session_id == session_id).all()
    responses = db.query(DBUserResponse).filter(DBUserResponse.session_id == session_id).all()
    feedback = db.query(DBInterviewFeedback).filter(DBInterviewFeedback.session_id == session_id).all()

    # Create the InterviewSession response object
    return {
        "session_id": past_interview.session_id,
        "questions": questions,
        "responses": responses,
        "feedback": feedback
    }

from fastapi import status

# Optional auth dependency
async def get_optional_user(current_user: Optional[User] = Depends(get_current_active_user)) -> Optional[User]:
    return current_user


@router.post("/start")
async def start_interview(
        position: str = Form(...),
        job_description: Optional[str] = Form(None),
        file: UploadFile = File(...),  # Resume is required
        db: Session = Depends(get_db),
        current_user: Optional[User] = None
):
    """Start a new interview with resume upload"""

    # Use provided user_id or default to 'anonymous'
    user_id = current_user.username if current_user else "anonymous"

    try:
        # Parse the resume
        from app.utils.file_utils import parser
        parsed_resume = parser(file)

        # Auto-set difficulty and question types (user doesn't choose)
        difficulty = "medium"
        q_types = ["behavioral", "technical"]

        session_id = str(uuid.uuid4())

        session = DBInterviewSession(
            session_id=session_id,
            user_id=user_id,
            position=position,
            job_description=job_description or "",
            difficulty=difficulty,
            question_types=q_types,
            start_time=datetime.now(),
            status="in_progress",
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        # Generate first question using resume context
        from app.prompts.interview_prompt import generate_interview_prompt_text

        prompt_template = generate_interview_prompt_text(
            resume=json.dumps(parsed_resume, indent=2),
            job_description=job_description or "",
            past_conversations="",
            position=position,
            difficulty=difficulty,
            question_type=", ".join(q_types)
        )

        result = gpt_service.call_gpt(prompt_template, temperature=0.6)

        if "error" in result:
            raise HTTPException(status_code=500, detail=f"OpenAI Error: {result['error']}")

        # Extract question from result
        question_text = result.get("raw_output") or result.get("question") or "Tell me about yourself."

        db_question = DBInterviewQuestion(
            session_id=session_id,
            question_id=str(uuid.uuid4()),
            question_text=question_text
        )

        # Initialize question_ids array with first question
        if session.question_ids is None:
            session.question_ids = []
        session.question_ids.append(db_question.question_id)

        db.add(db_question)
        db.commit()

        return {
            "session_id": session.session_id,
            "question_id": db_question.question_id,
            "question": question_text,
            "status": session.status,
        }

    except Exception as e:
        print("🔥 Interview start failed:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start mock interview: {str(e)}"
        )


@router.post("/answer")
async def submit_answer(
        question_id: str = Form(...),
        response_text: str = Form(...),
        file: UploadFile = File(...),  # Resume for context
        db: Session = Depends(get_db),
        current_user: Optional[User] = None
):
    """Submit answer to interview question"""

    # 1. Fetch the question
    question = db.query(DBInterviewQuestion).filter(DBInterviewQuestion.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    # 2. Fetch the session
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == question.session_id).first()
    if not session or session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Interview session not active.")

    # 3. Save the user's response
    db_response = DBUserResponse(
        session_id=session.session_id,
        question_id=question_id,
        response_text=response_text,
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)

    # 4. Parse resume for context
    from app.utils.file_utils import parser
    parsed_resume = parser(file)

    # 5. Build conversation history
    previous_conversation = ""
    previous_responses = db.query(DBUserResponse).filter(DBUserResponse.session_id == session.session_id).all()
    for response in previous_responses:
        q_text = db.query(DBInterviewQuestion).filter(
            DBInterviewQuestion.question_id == response.question_id).first().question_text
        previous_conversation += f"Question: {q_text}\nAnswer: {response.response_text}\n\n"

    # 6. Check if we should generate next question or end
    question_count = db.query(DBInterviewQuestion).filter(DBInterviewQuestion.session_id == session.session_id).count()
    MAX_QUESTIONS = 5

    if question_count < MAX_QUESTIONS:
        # Generate next question with resume context
        from app.prompts.interview_prompt import generate_interview_prompt_text

        next_question_prompt = generate_interview_prompt_text(
            resume=json.dumps(parsed_resume, indent=2),
            job_description=session.job_description or "",
            past_conversations=previous_conversation,
            position=session.position,
            difficulty=session.difficulty,
            question_type=", ".join(session.question_types)
        )

        next_result = gpt_service.call_gpt(next_question_prompt, temperature=0.6)
        next_question_text = next_result.get("raw_output") or next_result.get(
            "question") or "Tell me about a recent project."

        # Save next question
        new_question = DBInterviewQuestion(
            session_id=session.session_id,
            question_id=str(uuid.uuid4()),
            question_text=next_question_text
        )

        if session.question_ids is None:
            session.question_ids = []
        session.question_ids.append(new_question.question_id)

        db.add(new_question)
        db.commit()

        return {
            "type": "next_question",
            "next_question": {
                "id": new_question.question_id,
                "text": next_question_text
            }
        }

    else:
        # End interview
        session.status = "completed"
        session.end_time = datetime.utcnow()
        db.commit()

        # Generate final feedback
        feedback_prompt = f"Based on this interview conversation:\n\n{previous_conversation}\n\nProvide overall feedback on the candidate's performance."

        feedback_result = gpt_service.call_gpt(feedback_prompt)
        feedback_text = feedback_result.get("raw_output") or "Thank you for completing the interview."

        db_feedback = DBInterviewFeedback(
            session_id=session.session_id,
            feedback_text=feedback_text
        )
        db.add(db_feedback)
        db.commit()

        return {
            "type": "interview_complete",
            "feedback": feedback_text,
            "summary": {
                "questions_answered": question_count,
                "session_id": session.session_id,
                "end_time": session.end_time.isoformat()
            }
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
async def get_interview_feedback(session_id: str,
                                 current_user: User = Depends(get_current_active_user),
                                 db: Session = Depends(get_db)):
    """
    Get feedback for a completed interview session
    """
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    if not session and current_user.username != session_id:
        raise HTTPException(status_code=400, detail="Interview session not active.")

    feedback = db.query(DBInterviewFeedback).filter(DBInterviewFeedback.session_id == session_id).first()
    if not feedback:
        raise HTTPException(status_code=400, detail="No feedback found for this session.")

    return {
        "session_id": session_id,
        "feedback": feedback.feedback_text,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "duration": (session.end_time - session.start_time).total_seconds() / 60
    }
