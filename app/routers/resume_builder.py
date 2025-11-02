from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.resume_builder import ResumeBuilderRequest, ResumeBuilderResponse
from app.schemas.auth import User
from app.routers.auth import get_current_active_user
from app.services.resume_builder_service import resume_builder_service
from app.utils.resume_export import generate_resume_pdf, generate_resume_docx

router = APIRouter()


@router.post("/generate", response_model=ResumeBuilderResponse)
async def generate_resume(
    request: ResumeBuilderRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = None
):
    """
    Generate a professional resume based on user input using OpenAI
    """
    try:
        # Use authenticated user or provided user_id
        user_id = current_user.username if current_user else request.user_id or "anonymous"
        
        # Generate resume using AI service
        result = resume_builder_service.generate_resume(
            name=request.name,
            course=request.course,
            education_background=request.education_background,
            skills=request.skills,
            internship_experience=request.internship_experience,
            additional_info=request.additional_info or ""
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate resume")
            )
        
        return ResumeBuilderResponse(
            success=True,
            resume_text=result["resume_text"],
            suggestions=result.get("suggestions", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume generation failed: {str(e)}"
        )


@router.post("/preview")
async def preview_resume(request: ResumeBuilderRequest):
    """
    Generate a quick preview of the resume without saving
    """
    try:
        result = resume_builder_service.generate_resume(
            name=request.name,
            course=request.course,
            education_background=request.education_background,
            skills=request.skills,
            internship_experience=request.internship_experience,
            additional_info=request.additional_info or ""
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate preview")
            )
        
        return {
            "preview": result["resume_text"],
            "suggestions": result.get("suggestions", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Preview generation failed: {str(e)}"
        )


@router.post("/improve")
async def improve_resume_section(
    section: str,
    content: str,
    current_user: Optional[User] = None
):
    """
    Get AI suggestions to improve a specific resume section
    """
    try:
        # This could call a separate improvement service
        # For now, return a simple response
        return {
            "section": section,
            "original": content,
            "suggestions": [
                "Use more action verbs to start bullet points",
                "Add quantifiable metrics and achievements",
                "Be more specific about your contributions"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Improvement suggestions failed: {str(e)}"
        )


@router.post("/generate-pdf")
async def generate_resume_pdf_endpoint(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Generate a professional resume and return it as a PDF file
    For Bubble.io: Send body as {"name": "...", "course": "...", ...} directly
    """
    try:
        # Use payload directly (no 'data' wrapper needed for Raw body type)
        data = payload
        
        # Generate resume using AI service
        result = resume_builder_service.generate_resume(
            name=data.get("name", ""),
            course=data.get("course", ""),
            education_background=data.get("education_background", ""),
            skills=data.get("skills", ""),
            internship_experience=data.get("internship_experience", ""),
            additional_info=data.get("additional_info", "")
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate resume")
            )
        
        # Generate PDF from resume text
        pdf_content = generate_resume_pdf(
            resume_text=result["resume_text"],
            name=data.get("name", "Resume")
        )
        
        # Return PDF file
        filename = f"{data.get('name', 'Resume').replace(' ', '_')}_Resume.pdf"
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )


@router.post("/generate-docx")
async def generate_resume_docx_endpoint(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Generate a professional resume and return it as a DOCX file
    For Bubble.io: Send body as {"name": "...", "course": "...", ...} directly
    """
    try:
        # Use payload directly (no 'data' wrapper needed for Raw body type)
        data = payload
        
        # Generate resume using AI service
        result = resume_builder_service.generate_resume(
            name=data.get("name", ""),
            course=data.get("course", ""),
            education_background=data.get("education_background", ""),
            skills=data.get("skills", ""),
            internship_experience=data.get("internship_experience", ""),
            additional_info=data.get("additional_info", "")
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate resume")
            )
        
        # Generate DOCX from resume text
        docx_content = generate_resume_docx(
            resume_text=result["resume_text"],
            name=data.get("name", "Resume")
        )
        
        # Return DOCX file
        filename = f"{data.get('name', 'Resume').replace(' ', '_')}_Resume.docx"
        return Response(
            content=docx_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DOCX generation failed: {str(e)}"
        )
