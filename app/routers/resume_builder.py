from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.resume_builder import ResumeBuilderRequest, ResumeBuilderResponse
from app.schemas.auth import User
from app.routers.auth import get_current_active_user
from app.services.resume_builder_service import resume_builder_service

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
            major=request.major,
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
            major=request.major,
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
