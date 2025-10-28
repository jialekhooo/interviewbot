from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
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
    Retrieve all past interview sessions for a specific user.
    Fetch only the required columns and exclude unnecessary data.
    """
    # Select only the required columns from the InterviewSession table
    past_interview = db.query(DBInterviewSession.session_id).filter(DBInterviewSession.user_id == current_user.username).first()
    # Fetch related data for questions, responses, and feedback
    questions = db.query(DBInterviewQuestion).filter(DBInterviewQuestion.session_id == session_id).all()
    responses = db.query(DBUserResponse).filter(DBUserResponse.session_id == session_id).all()
    feedback = db.query(DBInterviewFeedback).filter(DBInterviewFeedback.session_id == session_id).all()

    # Create the InterviewSession response object
    return{
        "session_id":past_interview.session_id,
        "questions":questions,
        "responses":responses,
        "feedback":feedback
    }

from fastapi import status

# Optional auth dependency
async def get_optional_user(current_user: Optional[User] = Depends(get_current_active_user)) -> Optional[User]:
    return current_user

@router.post("/start")
async def start_interview(
    payload: StartInterviewSession = Depends(),
    db: Session = Depends(get_db),
    current_user: Optional[User] = None
):
    # Use provided user_id or default to 'anonymous'
    user_id = current_user.username if current_user else payload.user_id or "anonymous"
    
    # Skip user validation if not authenticated
    if current_user and payload.user_id and payload.user_id != current_user.username:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    try:
        position = payload.position
        difficulty = payload.difficulty
        q_types = payload.question_types or ["behavioral", "technical"]

        session_id = str(uuid.uuid4())

        session = DBInterviewSession(
            session_id=session_id,
            user_id=user_id,
            position=position,
            difficulty=difficulty,
            question_types=q_types,
            start_time=datetime.now(),
            status="in_progress",
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        # Call GPT
        system_prompt = f"You are a virtual interviewer for a {position} role."
        user_prompt = f"Start the interview by asking a {difficulty} level {q_types[0]} question."

        result = gpt_service.call_gpt_with_system(system_prompt, user_prompt)

        if "error" in result:
            raise HTTPException(status_code=500, detail=f"OpenAI Error: {result['error']}")

        question_text = result.get("raw_output") or result.get("question") or "Tell me about yourself."

        db_question = DBInterviewQuestion(session_id=session_id, question_id= str(uuid.uuid4()), question_text=question_text)

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
        print("🔥 Interview start failed:", str(e))  # This helps during dev
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start mock interview: {str(e)}"
        )


@router.post("/answer")
async def submit_answer(
        payload: UserResponse,
        db: Session = Depends(get_db),
        current_user: Optional[User] = None
):
    # 1. Fetch the question
    question = db.query(DBInterviewQuestion).filter(DBInterviewQuestion.question_id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    # 2. Fetch the session
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == question.session_id).first()
    if not session or session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Interview session not active.")

    # 3. Save the user's response
    db_response = DBUserResponse(
        session_id=session.session_id,
        question_id=payload.question_id,
        response_text=payload.response_text,
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)

    # 4. Build the history (all previous questions and responses)
    previous_conversation = ""
    previous_responses = db.query(DBUserResponse).filter(DBUserResponse.session_id == session.session_id).all()
    for response in previous_responses:
        question_text = db.query(DBInterviewQuestion).filter(
            DBInterviewQuestion.question_id == response.question_id).first().question_text
        previous_conversation += f"Question: {question_text}\nAnswer: {response.response_text}\n\n"

    # Add the current question and answer to the history
    previous_conversation += f"Question: {question.question_text}\nAnswer: {payload.response_text}\n\n"


    # 7. Check if we should generate a next question or end the interview
    question_count = db.query(DBInterviewQuestion).filter(DBInterviewQuestion.session_id == session.session_id).count()
    MAX_QUESTIONS = 5
    if question_count < MAX_QUESTIONS:
        # Generate next question based on the previous conversation history
        next_question_prompt = f"You are an interviewer. Based on the following interview history, ask the next appropriate question:\n\n{previous_conversation}\n\nAsk a {session.difficulty} level {session.question_types[0]} interview question for a {session.position} role."

        next_question_text = gpt_service.call_gpt(next_question_prompt).get("raw_output",
                                                                            "Tell me about a recent project.")

        # Save next question
        new_question = DBInterviewQuestion(
            session_id=session.session_id,
            question_id=str(uuid.uuid4()),
            question_text=next_question_text
        )

        # Update session question_ids with new question
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
        # Mark interview as complete
        session.status = "completed"
        session.end_time = datetime.utcnow()
        db.commit()

        # 5. Generate feedback using GPT (real or fake)
        prompt = f"You are an interviewer. Here's the conversation history so far:\n\n{previous_conversation}\n\nProvide feedback on the candidate's latest answer."

        gpt_result = gpt_service.call_gpt(prompt)
        feedback_text = gpt_result.get("raw_output") or gpt_result.get("feedback") or "Thanks for your response."

        # 6. Save the feedback
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
