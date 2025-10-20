from click import prompt
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import uuid
import json
import tempfile
from PyPDF2 import PdfReader
from docx import Document
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

@router.post("/analyze")
def analyze_resume(
    file: UploadFile = File(...),
    # current_user: User = Depends(get_current_active_user)
):
    # Ensure file has valid content
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload a .pdf or .docx file.")

    # Save uploaded file temporarily
    try:
        suffix = ".pdf" if file.filename.endswith(".pdf") else ".docx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            contents = file.file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    try:
        # Determine file type and parse accordingly
        if suffix == ".pdf":
            parsed_text = parse_pdf(temp_file_path)
        elif suffix == ".docx":
            parsed_text = parse_docx(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        with open("app/prompts/resume_parsing.txt", "r") as f:
            prompt_template = f.read()

        prompt_template = prompt_template.replace("resume_text", parsed_text)
        prompt_result = gpt_service.call_gpt(prompt_template, temperature=0.3)

        return {
            "file_name": file.filename,
            "analysis": prompt_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during file processing: {str(e)}")

    finally:
        # Clean up the temporary file
        try:
            os.remove(temp_file_path)
        except Exception:
            pass  # Avoid crashing on cleanup failure


def parse_pdf(file_path: str) -> str:
    try:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if not text:
            raise ValueError("No text could be extracted from the PDF.")
        return text
    except Exception as e:
        raise Exception(f"PDF parsing failed: {str(e)}")


def parse_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        if not text:
            raise ValueError("No text found in the DOCX file.")
        return text
    except Exception as e:
        raise Exception(f"DOCX parsing failed: {str(e)}")

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

# @router.post("/review")
# def get_resume_review(
#     file_id: str,
#     current_user: User = Depends(get_current_active_user),
#     job_description: str = None,
#     db: Session = Depends(get_db)
# ):
#     # Fetch resume from DB
#     db_resume = db.query(DBResume).filter(DBResume.file_id == file_id).first()
#
#     if current_user.username != db_resume.user_id:
#         raise HTTPException(status_code=404, detail="Review not found.")
#
#     if not db_resume:
#         raise HTTPException(status_code=404, detail="Resume not found")
#
#     parsed_resume = db_resume.analysis_result
#
#     if not parsed_resume:
#         raise HTTPException(status_code=400, detail="No parsed resume data available")
#
#     # Compose prompt with optional job description
#     with open("app/prompts/resume_improvement.txt", "r") as f:
#         prompt_template = f.read()
#
#     prompt_template = prompt_template.replace("resume_text", json.dumps(parsed_resume, indent=2))
#     prompt_template = prompt_template.replace("job_description", job_description or "")
#     system_prompt = "You are a professional and helpful assistant specialized in resume reviews."
#
#     # Call GPT service (using the global instance you defined)
#     response = gpt_service.call_gpt_with_system(system_prompt, prompt_template)
#
#     # Handle possible errors
#     if "error" in response:
#         raise HTTPException(status_code=500, detail=response["error"])
#
#     # Extract raw_output or fallback to string
#     review_text = response.get("raw_output") or str(response)
#     db_resume.review = review_text
#     db.commit()
#
#     return {"review": review_text}

@router.post("/review")
def get_resume_review(
    file: UploadFile = File(...),
    job_description: str = None,
):
    # Ensure file has valid content
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload a .pdf or .docx file.")

    # Save uploaded file temporarily
    try:
        suffix = ".pdf" if file.filename.endswith(".pdf") else ".docx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            contents = file.file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    try:
        # Determine file type and parse accordingly
        if suffix == ".pdf":
            parsed_text = parse_pdf(temp_file_path)
        elif suffix == ".docx":
            parsed_text = parse_docx(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

    # Compose prompt with optional job description
        with open("app/prompts/resume_improvement.txt", "r") as f:
            prompt_template = f.read()

        prompt_template = prompt_template.replace("resume_text", json.dumps(parsed_text, indent=2))
        prompt_template = prompt_template.replace("job_description", job_description or "")

        # Call GPT service (using the global instance you defined)
        prompt_result = gpt_service.call_gpt(prompt_template, temperature=0.3)

        return {"review": prompt_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during file processing: {str(e)}")
