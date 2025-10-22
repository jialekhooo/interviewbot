from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, UploadFile, File, Form
from typing import List, Dict
import json
from datetime import datetime

from app.services.interview_simulator import InterviewSimulator
from app.schemas.interview import InterviewSession, DifficultyLevel, QuestionType
from app.services.gpt_service import gpt_service
from app.prompts.interview_prompt import generate_interview_prompt_text
from app.prompts.feedback_prompt import generate_final_feedback_prompt_text

from app.utils.file_utils import parser

router = APIRouter()

# Store active interview sessions
active_sessions: Dict[str, InterviewSession] = {}

@router.get("/health")
async def interview_health():
    """Health check for interview service"""
    return {"status": "ok", "service": "interview", "active_sessions": len(active_sessions)}

from fastapi import status

@router.post("/start")
async def start_interview(
    position: str = Form(...),
    job_description: str = Form(""),
    difficulty: DifficultyLevel = Form(DifficultyLevel.MEDIUM),
    question_types: List[QuestionType] = Form(...),
    file: UploadFile = File(...),
    jd_file: UploadFile = File(None),  # NEW: Optional job description file
):
    try:
        q_types = question_types or ["behavioral", "technical"]
        
        # Parse resume
        parse_resume = parser(file)
        
        # Parse job description from file if provided, otherwise use form data
        if jd_file:
            try:
                job_desc_text = parser(jd_file)
            except Exception as e:
                print(f"Error parsing job description file: {e}")
                job_desc_text = job_description or ""
        else:
            job_desc_text = job_description or ""

        # Generate interview question with parsed JD
        prompt_template = generate_interview_prompt_text(
            json.dumps(parse_resume, indent=2), 
            job_desc_text,  # Use parsed job description
            "",
            position, 
            difficulty, 
            ", ".join(q_types)
        )
        print(prompt_template)
        result = gpt_service.call_gpt(prompt_template, temperature=0.6)

        if "error" in result:
            raise HTTPException(status_code=500, detail=f"OpenAI Error: {result['error']}")

        return {
            "question": result
        }

    except Exception as e:
        print("🔥 Interview start failed:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start mock interview: {str(e)}"
        )


@router.post("/answer")
async def submit_answer(
    position: str = Form(...),
    difficulty: DifficultyLevel = Form(DifficultyLevel.MEDIUM),
    job_description: str = Form(""),
    question_types: List[QuestionType] = Form(...),
    past_questions: str = Form(...),
    past_answers: str = Form(""),
    answer: str = Form(...),
    file: UploadFile = File(...),
    jd_file: UploadFile = File(None),  # NEW: Optional job description file
):
    q_types = question_types or ["behavioral", "technical"]
    
    # Parse resume
    parse_resume = parser(file)
    
    # Parse job description from file if provided, otherwise use form data
    if jd_file:
        try:
            job_desc_text = parser(jd_file)
        except Exception as e:
            print(f"Error parsing job description file: {e}")
            job_desc_text = job_description or ""
    else:
        job_desc_text = job_description or ""

    # Build the history (all previous questions and responses)
    previous_conversation = ""
    for question, ans in zip(past_questions.split("||,"), past_answers.split("||,") + [answer]):
        previous_conversation += f"Question: {question}\nAnswer: {ans}\n"
    print(previous_conversation)

    MAX_QUESTIONS = 5
    if len(past_answers.split("||,")) + 1 < MAX_QUESTIONS:
        # Compose prompt with parsed job description
        prompt_template = generate_interview_prompt_text(
            json.dumps(parse_resume, indent=2), 
            job_desc_text,  # Use parsed job description
            previous_conversation,
            position, 
            difficulty, 
            ", ".join(q_types)
        )

        result = gpt_service.call_gpt(prompt_template, temperature=0.6)

        if "error" in result:
            raise HTTPException(status_code=500, detail=f"OpenAI Error: {result['error']}")

        return {
            "question": result
        }

    else:
        return {
            "question": "End of Interview"
        }


@router.post("/feedback")
async def get_interview_feedback(
    position: str = Form(...),
    difficulty: DifficultyLevel = Form(DifficultyLevel.MEDIUM),
    job_description: str = Form(""),
    question_types: List[QuestionType] = Form(...),
    past_questions: str = Form(...),
    past_answers: str = Form(...),
    file: UploadFile = File(...),
    jd_file: UploadFile = File(None),  # NEW: Optional job description file
):
    """
    Get feedback for a completed interview session
    """
    q_types = question_types or ["behavioral", "technical"]
    
    # Parse resume
    parse_resume = parser(file)
    
    # Parse job description from file if provided, otherwise use form data
    if jd_file:
        try:
            job_desc_text = parser(jd_file)
        except Exception as e:
            print(f"Error parsing job description file: {e}")
            job_desc_text = job_description or ""
    else:
        job_desc_text = job_description or ""

    previous_conversation = ""
    for question, ans in zip(past_questions.split("||,"), past_answers.split("||,")):
        previous_conversation += f"Question: {question}\nAnswer: {ans}\n"
    print(previous_conversation)

    prompt_template = generate_final_feedback_prompt_text(
        json.dumps(parse_resume, indent=2), 
        job_desc_text,  # Use parsed job description
        previous_conversation,
        position, 
        difficulty, 
        ", ".join(q_types)
    )

    result = gpt_service.call_gpt(prompt_template, temperature=0.6)

    if "error" in result:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {result['error']}")

    return {
        "feedback": result
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
