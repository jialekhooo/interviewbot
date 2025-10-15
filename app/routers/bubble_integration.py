from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from app.services.gpt_service import gpt_service
import os

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
        
        # Generate first question (simplified for now)
        question_text = "Tell me about yourself and your background."
        
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
        # Generate feedback (simplified for now)
        feedback_text = "FEEDBACK: Good answer! Keep practicing.\nSCORE: 7\nNEXT_QUESTION: What are your career goals?"
        
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
async def bubble_generate_resume(request: BubbleResumeGenerate):
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
            skills_md = ''.join([f"\n- {s}" for s in skills_list]) if skills_list else (f"\n- {request.skills}" if request.skills else "")
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

        return SimpleResponse(
            success=True,
            message="Resume generated successfully",
            data={
                "resume_text": resume_text,
                "format": "markdown",
            }
        )
    except Exception as e:
        return SimpleResponse(
            success=False,
            message=f"Failed to generate resume: {str(e)}",
            data={}
        )

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
            "endpoints": [
                "/api/bubble/interview/start",
                "/api/bubble/interview/answer",
                "/api/bubble/resume/analyze",
                "/api/bubble/resume/generate",
                "/api/bubble/guidance/improve"
            ]
        }
    )
