from click import prompt
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import List
import os
import uuid
import json
import tempfile
from PyPDF2 import PdfReader
from docx import Document
from datetime import datetime
from app.utils.file_utils import parser
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

def clean_review_output(text):
    """
    Clean up the review text by properly formatting newlines and structure
    """
    if not text:
        return ""
    
    # Handle both dict and string responses
    if isinstance(text, dict):
        # If it's a structured response, extract the raw_output
        text = text.get("raw_output", str(text))
    
    # Convert to string if not already
    text = str(text)
    
    # Replace literal \n with actual newlines
    text = text.replace('\\n', '\n')
    
    # Remove excessive newlines (more than 2 consecutive)
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Split into sections and clean each
    sections = text.split('\n\n')
    cleaned_sections = []
    
    for section in sections:
        # Remove leading/trailing whitespace
        section = section.strip()
        if not section:
            continue
            
        # If it's a header (short line, possibly with special chars)
        if len(section) < 100 and (section.isupper() or section.endswith(':') or section.startswith('#')):
            cleaned_sections.append(f"\n{section}\n")
        else:
            # Regular paragraph - ensure proper spacing
            cleaned_sections.append(section)
    
    # Join sections with proper spacing
    result = '\n\n'.join(cleaned_sections)
    
    # Final cleanup
    result = result.strip()
    
    return result

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
):
    parsed_text = parser(file)

    with open("app/prompts/resume_parsing.txt", "r") as f:
        prompt_template = f.read()

    prompt_template = prompt_template.replace("resume_text", json.dumps(parsed_text, indent=2))
    prompt_result = gpt_service.call_gpt(prompt_template, temperature=0.3)

    return {
        "file_name": file.filename,
        "analysis": prompt_result
    }

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
    job_description: str = Form(""),
    file: UploadFile = File(...),
):
    parsed_text = parser(file)
    
    # Compose prompt with optional job description
    with open("app/prompts/resume_improvement.txt", "r") as f:
        prompt_template = f.read()

    prompt_template = prompt_template.replace("resume_text", json.dumps(parsed_text, indent=2))
    prompt_template = prompt_template.replace("job_description", job_description or "")

    # Enhanced system prompt for better formatting
    system_prompt = """You are a professional resume consultant providing clear, actionable feedback. 

Structure your response in clear sections with proper headings:
- Use clear section headers
- Write in complete, well-formed paragraphs
- Use bullet points for lists of specific improvements
- Provide specific examples
- Keep language professional but friendly

Format your response with proper spacing between sections."""

    # # Call GPT service
    # prompt_result = gpt_service.call_gpt_with_system(system_prompt, prompt_template, temperature=0.4)
    #
    # # Clean the output
    # review_text = clean_review_output(prompt_result)
    #
    # return {
    #     "review": review_text,
    #     "formatted": True  # Flag to indicate this is pre-formatted
    # }
    # Call GPT service (using the global instance you defined)
    prompt_result = gpt_service.call_gpt(prompt_template, temperature=0.3)

    return prompt_result

