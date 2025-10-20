from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
from ..services.gpt_service import gpt_service
from ..utils.prompt_utils import fill_prompt
import PyPDF2
import io
import chardet

router = APIRouter()

class ResumeImprovementRequest(BaseModel):
    resume_text: str
    target_role: str = ""
    experience_level: str = "mid"

class ImprovementSuggestion(BaseModel):
    category: str
    current_issue: str
    suggestion: str
    priority: str

class ResumeImprovementResponse(BaseModel):
    overall_score: float
    improvements: List[ImprovementSuggestion]
    summary: str
    strengths: List[str]

@router.post("/analyze", response_model=ResumeImprovementResponse)
async def analyze_resume_for_improvement(request: ResumeImprovementRequest):
    """
    Analyze a resume and provide detailed improvement suggestions
    """
    try:
        # Use the resume improvement prompt template
        prompt = fill_prompt(
            "resume_improvement",
            resume_text=request.resume_text,
            target_role=request.target_role or "software engineering position",
            experience_level=request.experience_level
        )
        
        result = gpt_service.call_gpt(prompt, temperature=0.6)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"AI service error: {result['error']}")
        
        # Parse the response
        if "raw_output" in result:
            # Fallback response
            return ResumeImprovementResponse(
                overall_score=7.0,
                improvements=[
                    ImprovementSuggestion(
                        category="General",
                        current_issue="Resume needs improvement",
                        suggestion=result["raw_output"],
                        priority="medium"
                    )
                ],
                summary="Resume analysis completed. See detailed suggestions above.",
                strengths=["Experience shown", "Education included"]
            )
        
        # Parse structured response
        improvements = []
        if "improvements" in result:
            for imp in result["improvements"]:
                improvements.append(ImprovementSuggestion(
                    category=imp.get("category", "General"),
                    current_issue=imp.get("issue", ""),
                    suggestion=imp.get("suggestion", ""),
                    priority=imp.get("priority", "medium")
                ))
        
        return ResumeImprovementResponse(
            overall_score=result.get("score", 7.0),
            improvements=improvements,
            summary=result.get("summary", "Resume analysis completed"),
            strengths=result.get("strengths", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze resume: {str(e)}")

@router.post("/upload-analyze")
async def upload_and_analyze_resume(
    file: UploadFile = File(...),
    target_role: str = "",
    experience_level: str = "mid"
):
    """
    Upload a resume file and get improvement suggestions
    """
    try:
        # Read file content
        content = await file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        elif file.filename.lower().endswith(('.txt', '.doc', '.docx')):
        # Attempt to detect encoding of the file content using chardet
            detected_encoding = chardet.detect(content)['encoding']
            try:
                text = content.decode(detected_encoding)
            except UnicodeDecodeError:
                raise HTTPException(status_code=400,
                                    detail=f"Could not decode file with encoding {detected_encoding}.")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, TXT, DOC, or DOCX files.")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file.")
        
        # Analyze the extracted text
        request = ResumeImprovementRequest(
            resume_text=text,
            target_role=target_role,
            experience_level=experience_level
        )
        
        return await analyze_resume_for_improvement(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded resume: {str(e)}")

@router.post("/parse")
async def parse_resume_details(request: ResumeImprovementRequest):
    """
    Parse resume and extract structured information
    """
    try:
        # Use the resume parsing prompt template
        prompt = fill_prompt(
            "resume_parsing",
            resume_text=request.resume_text
        )
        
        result = gpt_service.call_gpt(prompt, temperature=0.3)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"AI service error: {result['error']}")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

@router.get("/health")
async def improvement_health():
    """Health check for resume improvement service"""
    return {"status": "ok", "service": "resume_improvement"}
