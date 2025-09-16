from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import uuid
from datetime import datetime
from ..services.resume_parser import parse_resume
from ..schemas.resume import ResumeAnalysisResponse

router = APIRouter()

# Directory to store uploaded resumes
UPLOAD_DIR = "data/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=ResumeAnalysisResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume file (PDF or DOCX)
    """
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.pdf', '.docx']:
            raise HTTPException(status_code=400, detail="File type not supported. Please upload a PDF or DOCX file.")
        
        # Save the file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse the resume
        analysis = parse_resume(file_path)
        
        return {
            "file_id": file_id,
            "file_name": file.filename,
            "uploaded_at": datetime.utcnow().isoformat(),
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@router.get("/analysis/{file_id}")
async def get_resume_analysis(file_id: str):
    """
    Get analysis for a previously uploaded resume
    """
    # Implementation will be added later
    return {"message": "Resume analysis endpoint"}

@router.post("/review")
async def get_resume_review(file_id: str, job_description: str = None):
    """
    Get detailed review of a resume, optionally tailored to a job description
    """
    # Implementation will be added later
    return {"message": "Resume review endpoint"}
