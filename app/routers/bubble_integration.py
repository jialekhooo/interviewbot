from fastapi import APIRouter, HTTPException, Header, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from app.services.gpt_service import gpt_service
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.gpt_result import DBGPTResult
import os
import tempfile
import shutil


def verify_bubble_api_key(
        x_api_key: Optional[str] = Header(None),
        authorization: Optional[str] = Header(None),
):
    """Require API key if BUBBLE_API_KEY is set.
    Accepts either X-API-Key: <key> or Authorization: Bearer <key>.
    """
    expected = os.getenv("BUBBLE_API_KEY")
    if not expected:
        return  # public if not configured

    supplied: Optional[str] = None
    if x_api_key:
        supplied = x_api_key.strip()
    elif authorization and authorization.lower().startswith("bearer "):
        supplied = authorization[7:].strip()

    if not supplied or supplied != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")


router = APIRouter(dependencies=[Depends(verify_bubble_api_key)])


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


class BubbleResumeGenerate(BaseModel):
    name: str
    major: str
    education_background: str
    skills: str
    internship_experience: str = ""
    additional: str = ""
    user_id: Optional[str] = None


class BubbleGuidance(BaseModel):
    question: str
    user_answer: str
    context: str = ""


class BubbleResultsList(BaseModel):
    user_id: Optional[str] = None
    category: Optional[str] = None
    limit: int = 20
    offset: int = 0


class BubbleSaveResult(BaseModel):
    category: str
    output_text: str
    user_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None


# Simple response models for Bubble.io
class SimpleResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] = {}


# ============================================================================
# INTERVIEW ENDPOINTS - TEXT AND REALISTIC MODE
# ============================================================================

@router.post("/interview/start", response_model=SimpleResponse)
async def bubble_start_interview(
        user_id: str = Form(...),
        position: str = Form(...),
        job_description: str = Form(""),
        interview_mode: str = Form("text"),  # "text" or "realistic"
        resume_file: UploadFile = File(...)
):
    """
    Start an interview session (works for both text and realistic modes)

    Bubble.io Usage:
    - API Call: POST /api/bubble/interview/start
    - Content-Type: multipart/form-data
    - Fields:
      - user_id (text)
      - position (text)
      - job_description (text, optional)
      - interview_mode (text: "text" or "realistic")
      - resume_file (file: PDF or DOCX)

    Returns:
    {
      "success": true,
      "message": "Interview started successfully",
      "data": {
        "session_id": "uuid",
        "question_id": "uuid",
        "question": "Tell me about yourself and your background.",
        "interview_mode": "text",
        "position": "Software Engineer",
        "question_number": 1,
        "max_questions": 5
      }
    }
    """
    try:
        # Validate file type
        if not resume_file.filename.lower().endswith(('.pdf', '.docx')):
            return SimpleResponse(
                success=False,
                message="Resume must be PDF or DOCX format",
                data={}
            )

        # Parse resume
        from app.utils.file_utils import parser
        parsed_resume = parser(resume_file)

        # HARDCODED FIRST QUESTION - Self Introduction
        first_question = f"Tell me about yourself and your background. What interests you about the {position} position?"

        # Create session
        session_id = str(uuid.uuid4())
        question_id = str(uuid.uuid4())

        return SimpleResponse(
            success=True,
            message="Interview started successfully",
            data={
                "session_id": session_id,
                "question_id": question_id,
                "question": first_question,
                "interview_mode": interview_mode,
                "position": position,
                "question_number": 1,
                "max_questions": 5
            }
        )

    except Exception as e:
        return SimpleResponse(
            success=False,
            message=f"Failed to start interview: {str(e)}",
            data={}
        )


@router.post("/interview/submit-answer", response_model=SimpleResponse)
async def bubble_submit_answer(
        session_id: str = Form(...),
        question_id: str = Form(...),
        answer_text: str = Form(...),
        position: str = Form(...),
        job_description: str = Form(""),
        past_questions: str = Form(""),  # Delimited by "||,"
        past_answers: str = Form(""),  # Delimited by "||,"
        resume_file: UploadFile = File(...),
        # Optional: For realistic mode
        words_per_minute: Optional[int] = Form(None),
        filler_words_count: Optional[int] = Form(None),
        confidence_score: Optional[int] = Form(None),
        eye_contact_score: Optional[int] = Form(None),
        engagement_score: Optional[int] = Form(None)
):
    """
    Submit an answer and get next question or feedback
    Works for BOTH text and realistic interview modes

    Bubble.io Usage:
    - API Call: POST /api/bubble/interview/submit-answer
    - Content-Type: multipart/form-data
    - Required Fields:
      - session_id (text)
      - question_id (text)
      - answer_text (text)
      - position (text)
      - job_description (text, can be empty)
      - past_questions (text: questions joined by "||,")
      - past_answers (text: answers joined by "||,")
      - resume_file (file)
    - Optional Fields (for realistic mode):
      - words_per_minute (number)
      - filler_words_count (number)
      - confidence_score (number, 0-100)
      - eye_contact_score (number, 0-100)
      - engagement_score (number, 0-100)

    Returns (In Progress):
    {
      "success": true,
      "message": "Answer received, next question generated",
      "data": {
        "status": "in_progress",
        "next_question_id": "uuid",
        "next_question": "Next question text",
        "question_number": 2,
        "max_questions": 5
      }
    }

    Returns (Completed):
    {
      "success": true,
      "message": "Interview completed",
      "data": {
        "status": "completed",
        "final_feedback": "Overall feedback...",
        "strengths": ["Strength 1", "Strength 2"],
        "areas_for_improvement": ["Area 1", "Area 2"],
        "overall_assessment": "Assessment text",
        "sample_answers": ["Answer 1", "Answer 2"],
        "performance_summary": {...},
        "questions_answered": 5
      }
    }
    """
    try:
        # Parse resume
        from app.utils.file_utils import parser
        parsed_resume = parser(resume_file)

        # Build conversation history
        questions_list = past_questions.split("||,") if past_questions else []
        answers_list = past_answers.split("||,") if past_answers else []

        # Add current answer
        answers_list.append(answer_text)

        conversation_history = ""
        for q, a in zip(questions_list, answers_list):
            if q and a:
                conversation_history += f"Question: {q}\nAnswer: {a}\n\n"

        # Check if interview should continue
        MAX_QUESTIONS = 5
        question_count = len(questions_list)

        if question_count >= MAX_QUESTIONS:
            # Generate final feedback
            from app.prompts.feedback_prompt import generate_final_feedback_prompt_text
            import json

            feedback_prompt = generate_final_feedback_prompt_text(
                resume=json.dumps(parsed_resume, indent=2),
                job_description=job_description,
                past_conversations=conversation_history,
                position=position
            )

            feedback_result = gpt_service.call_gpt(feedback_prompt, temperature=0.6)

            # Parse feedback
            final_feedback = feedback_result.get("final_feedback") or feedback_result.get("raw_output",
                                                                                          "Thank you for completing the interview!")
            strengths = feedback_result.get("strengths", [])
            improvements = feedback_result.get("areas_for_improvement", [])
            assessment = feedback_result.get("overall_assessment", "")
            sample_answers = feedback_result.get("sample_answers", [])

            # Ensure lists are always lists
            if not isinstance(strengths, list):
                strengths = [str(strengths)] if strengths else []
            if not isinstance(improvements, list):
                improvements = [str(improvements)] if improvements else []
            if not isinstance(sample_answers, list):
                sample_answers = [str(sample_answers)] if sample_answers else []

            # Include performance metrics if realistic mode
            performance_summary = {}
            if words_per_minute is not None:
                performance_summary["speech_analysis"] = {
                    "words_per_minute": words_per_minute,
                    "filler_words": filler_words_count or 0,
                    "confidence": confidence_score or 0
                }

            if eye_contact_score is not None:
                performance_summary["visual_analysis"] = {
                    "eye_contact": eye_contact_score,
                    "engagement": engagement_score or 0
                }

            return SimpleResponse(
                success=True,
                message="Interview completed",
                data={
                    "status": "completed",
                    "final_feedback": final_feedback,
                    "strengths": strengths,
                    "areas_for_improvement": improvements,
                    "overall_assessment": assessment,
                    "sample_answers": sample_answers,
                    "performance_summary": performance_summary,
                    "questions_answered": question_count
                }
            )

        else:
            # Generate next question
            from app.prompts.interview_prompt import generate_interview_prompt_text
            import json

            next_prompt = generate_interview_prompt_text(
                resume=json.dumps(parsed_resume, indent=2),
                job_description=job_description,
                past_conversations=conversation_history,
                position=position,
                first=False
            )

            next_result = gpt_service.call_gpt(next_prompt, temperature=0.6)

            next_question = next_result.get("question") or next_result.get("raw_output",
                                                                           "Tell me more about your experience.")
            sample_answer = next_result.get("sample_answer", "")

            return SimpleResponse(
                success=True,
                message="Answer received, next question generated",
                data={
                    "status": "in_progress",
                    "next_question_id": str(uuid.uuid4()),
                    "next_question": next_question,
                    "sample_answer": sample_answer,
                    "question_number": question_count + 1,
                    "max_questions": MAX_QUESTIONS
                }
            )

    except Exception as e:
        return SimpleResponse(
            success=False,
            message=f"Failed to process answer: {str(e)}",
            data={}
        )


@router.get("/interview/status/{session_id}", response_model=SimpleResponse)
async def bubble_interview_status(session_id: str):
    """
    Get interview session status

    Bubble.io Usage:
    - API Call: GET /api/bubble/interview/status/{session_id}
    """
    try:
        # In production, fetch from database
        return SimpleResponse(
            success=True,
            message="Session status retrieved",
            data={
                "session_id": session_id,
                "status": "in_progress",
                "questions_answered": 0,
                "max_questions": 5
            }
        )
    except Exception as e:
        return SimpleResponse(
            success=False,
            message=f"Failed to get status: {str(e)}",
            data={}
        )


@router.get("/interview/templates", response_model=SimpleResponse)
async def bubble_interview_templates():
    """
    Get interview question templates for different positions

    Bubble.io Usage:
    - API Call: GET /api/bubble/interview/templates

    Returns sample questions you can show to users
    """
    templates = {
        "Software Engineer": [
            "Tell me about yourself and your background.",
            "Describe a challenging coding problem you solved recently.",
            "How do you approach debugging complex issues?",
            "What's your experience with version control systems?",
            "Tell me about a time you had to learn a new technology quickly."
        ],
        "Product Manager": [
            "Tell me about yourself and your product management experience.",
            "How do you prioritize features in a product roadmap?",
            "Describe a time you had to make a difficult product decision.",
            "How do you handle conflicting stakeholder requirements?",
            "What metrics do you use to measure product success?"
        ],
        "Data Scientist": [
            "Tell me about yourself and your data science background.",
            "Explain a machine learning project you've worked on.",
            "How do you handle missing data in your analyses?",
            "Describe your experience with data visualization.",
            "How do you communicate technical findings to non-technical stakeholders?"
        ],
        "General": [
            "Tell me about yourself.",
            "What are your greatest strengths and weaknesses?",
            "Describe a challenging situation and how you overcame it.",
            "Where do you see yourself in 5 years?",
            "Why do you want this position?"
        ]
    }

    return SimpleResponse(
        success=True,
        message="Interview templates retrieved",
        data={"templates": templates}
    )


# ============================================================================
# EXISTING ENDPOINTS (RESUME, GUIDANCE, ETC.)
# ============================================================================

@router.post("/resume/analyze", response_model=SimpleResponse)
async def bubble_analyze_resume(request: BubbleResumeAnalysis):
    """
    Bubble.io friendly resume analysis
    """
    try:
        # Simplified resume analysis for now
        analysis = f"Resume analysis for {request.target_role or 'software engineering'}: Your resume shows good experience. Consider adding more specific achievements and metrics to strengthen your application."

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


@router.post("/resume/generate", response_model=SimpleResponse)
async def bubble_generate_resume(request: BubbleResumeGenerate, db: Session = Depends(get_db)):
    try:
        system_prompt = "You are an expert resume writer who creates clear, concise, and professional resumes. Output should be a well-formatted Markdown resume with clear section headers and bullet points."
        skills_list = [s.strip() for s in request.skills.split(',') if s.strip()]
        user_prompt = (
            "Generate a professional resume using the following details.\n"
            f"Name: {request.name}\n"
            f"Major: {request.major}\n"
            f"Education Background: {request.education_background}\n"
            f"Skills: {', '.join(skills_list) if skills_list else request.skills}\n"
            f"Internship Experience: {request.internship_experience}\n"
            f"Additional: {request.additional}\n\n"
            "Format: Markdown.\n"
            "Sections: Header with name, Professional Summary, Education, Skills (bullet list), Experience (bullet points with impact and metrics), Projects (optional if relevant), Additional."
        )

        ai = gpt_service.call_gpt_with_system(system_prompt, user_prompt, temperature=0.6)
        resume_text = ai.get("raw_output") if isinstance(ai, dict) else None

        # Fallback if AI unavailable or output isn't resume-like
        if (
                not resume_text
                or len(resume_text) < 100
                or (
                "## Education" not in resume_text
                and "## Skills" not in resume_text
                and "## Experience" not in resume_text
        )
        ):
            skills_md = ''.join([f"\n- {s}" for s in skills_list]) if skills_list else (
                f"\n- {request.skills}" if request.skills else "")
            resume_text = (
                f"# {request.name}\n\n"
                f"**Major:** {request.major}\n\n"
                f"## Professional Summary\n"
                f"Motivated {request.major} candidate with strong academic background and hands-on internship experience. Detail-oriented, quick learner, and passionate about solving real-world problems.\n\n"
                f"## Education\n{request.education_background}\n\n"
                f"## Skills{skills_md}\n\n"
                f"## Experience\n- {request.internship_experience or 'Internship details not provided.'}\n\n"
                f"## Additional\n- {request.additional or 'N/A'}\n"
            )
        # persist result
        result_meta: Dict[str, Any] = {}
        try:
            record = DBGPTResult(
                user_id=request.user_id or None,
                category="resume",
                input_data=request.dict(),
                output_text=resume_text,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            result_meta = {"result_id": record.id, "created_at": record.created_at.isoformat()}
        except Exception:
            result_meta = {}

        return SimpleResponse(
            success=True,
            message="Resume generated successfully",
            data={
                "resume_text": resume_text,
                "format": "markdown",
                "result_id": result_meta.get("result_id"),
                "created_at": result_meta.get("created_at"),
            }
        )
    except Exception as e:
        return SimpleResponse(
            success=False,
            message=f"Failed to generate resume: {str(e)}",
            data={}
        )


@router.post("/results/list", response_model=SimpleResponse)
async def bubble_list_results(request: BubbleResultsList, db: Session = Depends(get_db)):
    try:
        q = db.query(DBGPTResult)
        if request.user_id:
            q = q.filter(DBGPTResult.user_id == request.user_id)
        if request.category:
            q = q.filter(DBGPTResult.category == request.category)
        limit = min(max(request.limit, 1), 100)
        offset = max(request.offset, 0)
        rows = q.order_by(DBGPTResult.created_at.desc()).offset(offset).limit(limit).all()
        items = [
            {
                "id": r.id,
                "user_id": r.user_id,
                "category": r.category,
                "output_text": r.output_text,
                "input_data": r.input_data,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
        return SimpleResponse(success=True, message="Results fetched", data={"items": items, "count": len(items)})
    except Exception as e:
        return SimpleResponse(success=False, message=f"Failed to list results: {str(e)}", data={})


@router.get("/results/{result_id}", response_model=SimpleResponse)
async def bubble_get_result(result_id: int, db: Session = Depends(get_db)):
    try:
        r = db.query(DBGPTResult).filter(DBGPTResult.id == result_id).first()
        if not r:
            raise HTTPException(status_code=404, detail="Result not found")
        return SimpleResponse(
            success=True,
            message="Result fetched",
            data={
                "id": r.id,
                "user_id": r.user_id,
                "category": r.category,
                "output_text": r.output_text,
                "input_data": r.input_data,
                "created_at": r.created_at.isoformat(),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        return SimpleResponse(success=False, message=f"Failed to fetch result: {str(e)}", data={})


@router.post("/results/save", response_model=SimpleResponse)
async def bubble_save_result(request: BubbleSaveResult, db: Session = Depends(get_db)):
    try:
        row = DBGPTResult(
            user_id=request.user_id,
            category=request.category,
            input_data=request.input_data,
            output_text=request.output_text,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return SimpleResponse(success=True, message="Saved",
                              data={"result_id": row.id, "created_at": row.created_at.isoformat()})
    except Exception as e:
        return SimpleResponse(success=False, message=f"Failed to save: {str(e)}", data={})


@router.post("/guidance/improve", response_model=SimpleResponse)
async def bubble_get_guidance(request: BubbleGuidance):
    """
    Bubble.io friendly answer guidance
    """
    try:
        # Simplified guidance for now
        guidance = f"For the question '{request.question}', your answer shows good understanding. To improve, try adding more specific examples and quantifiable results from your experience."

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
            "available_modes": ["text", "realistic"],
            "endpoints": [
                "/api/bubble/interview/start",
                "/api/bubble/interview/submit-answer",
                "/api/bubble/interview/status/{session_id}",
                "/api/bubble/interview/templates",
                "/api/bubble/resume/analyze",
                "/api/bubble/resume/generate",
                "/api/bubble/guidance/improve"
            ]
        }
    )