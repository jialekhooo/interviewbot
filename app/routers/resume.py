from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import get_current_active_user

from app.schemas.auth import User
from app.schemas.resume import ResumeAnalysisResponse
from app.models.resume import DBResume

from app.services.resume_parser import parse_resume
from app.services.gpt_service import gpt_service

router = APIRouter()

# Directory to store uploaded resumes
UPLOAD_DIR = "data/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.pdf', '.docx']:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        resume_record = DBResume(
            file_id=file_id,
            file_name=file.filename,
            file_path=file_path,
            user_id=current_user.username,
        )
        db.add(resume_record)
        db.commit()

        return {
            "file_id": file_id,
            "file_name": file.filename,
            "status": "success",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
@router.post("/analysis/{file_id}", response_model=ResumeAnalysisResponse)
def analyze_resume(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resume = db.query(DBResume).filter(DBResume.file_id == str(file_id)).first()
    if not resume and resume.user_id != current_user.username:
        raise HTTPException(status_code=404, detail="Resume not found.")
    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="File not found on server.")

    try:
        parsed_data = parse_resume(resume.file_path)
        resume.analysis_result = parsed_data
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")

    return ResumeAnalysisResponse(
        file_id=resume.file_id,
        file_name=resume.file_name,
        uploaded_at=resume.uploaded_at.isoformat(),
        analysis=resume.analysis_result
    )

from typing import List

@router.get("/past-analysis/{user_id}", response_model=List[ResumeAnalysisResponse])
def get_past_analysis(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    resumes = db.query(DBResume).filter(DBResume.user_id == user_id).all()

    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found for this user.")

    return [
        ResumeAnalysisResponse(
            file_id=r.file_id,
            file_name=r.file_name,
            uploaded_at=r.uploaded_at.isoformat(),
            analysis=r.analysis_result or {}
        )
        for r in resumes
    ]

@router.post("/review")
def get_resume_review(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    job_description: str = None,
    db: Session = Depends(get_db)
):
    # Fetch resume from DB
    db_resume = db.query(DBResume).filter(DBResume.file_id == file_id).first()

    if current_user.username != db_resume.user_id:
        raise HTTPException(status_code=404, detail="Review not found.")

    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    parsed_resume = db_resume.analysis_result
    if not parsed_resume:
        raise HTTPException(status_code=400, detail="No parsed resume data available")

    # Compose prompt with optional job description
    user_prompt = (
        "You are a career coach assistant. Provide a detailed review of the following resume:\n\n"
        + json.dumps(parsed_resume, indent=2)
    )
    if job_description:
        user_prompt += "\n\nJob Description:\n" + job_description
    user_prompt += "\n\nPlease give constructive feedback highlighting strengths, weaknesses, and suggestions for improvement."

    system_prompt = "You are a helpful assistant specialized in resume reviews."

    # Call GPT service (using the global instance you defined)
    response = gpt_service.call_gpt_with_system(system_prompt, user_prompt)

    # Handle possible errors
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])

    # Extract raw_output or fallback to string
    review_text = response.get("raw_output") or str(response)
    db_resume.review = review_text
    db.commit()

    return {"review": review_text}
