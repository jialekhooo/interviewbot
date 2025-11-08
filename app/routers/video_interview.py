from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import os
import shutil
from datetime import datetime

from app.database import get_db
from app.models.video_interview import DBVideoInterview
from app.schemas.video_interview import (
    VideoInterviewCreate,
    VideoInterviewResponse,
    VideoAnalysisResult
)
from app.schemas.auth import User
from app.routers.auth import get_current_active_user
from app.services.video_analysis_service import video_analysis_service

router = APIRouter()

# Directory for storing uploaded videos
UPLOAD_DIR = "static/video_interviews"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/create", response_model=VideoInterviewResponse)
async def create_video_interview_session(
    payload: VideoInterviewCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new video interview session
    """
    # Use authenticated user or provided user_id
    user_id = current_user.username if current_user else payload.user_id
    
    session_id = str(uuid.uuid4())
    
    video_interview = DBVideoInterview(
        session_id=session_id,
        user_id=user_id,
        position=payload.position,
        question_text=payload.question_text,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    db.add(video_interview)
    db.commit()
    db.refresh(video_interview)
    
    return video_interview


@router.post("/upload/{session_id}")
async def upload_video(
    session_id: str,
    video: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Upload video file for a video interview session
    """
    # Fetch the session
    video_interview = db.query(DBVideoInterview).filter(
        DBVideoInterview.session_id == session_id
    ).first()
    
    if not video_interview:
        raise HTTPException(status_code=404, detail="Video interview session not found")
    
    # Verify user ownership if authenticated
    if current_user and video_interview.user_id != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to upload to this session")
    
    # Validate file type
    allowed_types = ["video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"]
    if video.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Save video file
    file_extension = video.filename.split('.')[-1]
    filename = f"{session_id}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")
    
    # Update database
    video_interview.video_path = file_path
    video_interview.status = "processing"
    db.commit()
    
    # Process video in background
    if background_tasks:
        background_tasks.add_task(
            process_video_interview,
            session_id=session_id,
            video_path=file_path,
            question=video_interview.question_text,
            position=video_interview.position,
            db=db
        )
    
    return {
        "message": "Video uploaded successfully",
        "session_id": session_id,
        "status": "processing"
    }


async def process_video_interview(
    session_id: str,
    video_path: str,
    question: str,
    position: str,
    db: Session
):
    """
    Background task to process video interview
    """
    try:
        # Analyze the video
        analysis_result = video_analysis_service.analyze_video_interview(
            video_path=video_path,
            question=question,
            position=position
        )
        
        # Update database with results
        video_interview = db.query(DBVideoInterview).filter(
            DBVideoInterview.session_id == session_id
        ).first()
        
        if video_interview:
            if analysis_result.get("success"):
                video_interview.transcript = analysis_result.get("transcript", "")
                video_interview.feedback = analysis_result.get("feedback", "")
                video_interview.scores = analysis_result.get("scores", {})
                video_interview.analysis = analysis_result.get("analysis", {})
                video_interview.status = "completed"
            else:
                video_interview.status = "failed"
                video_interview.feedback = analysis_result.get("error", "Analysis failed")
            
            db.commit()
    
    except Exception as e:
        print(f"Error processing video interview: {e}")
        video_interview = db.query(DBVideoInterview).filter(
            DBVideoInterview.session_id == session_id
        ).first()
        if video_interview:
            video_interview.status = "failed"
            video_interview.feedback = f"Processing error: {str(e)}"
            db.commit()


@router.get("/status/{session_id}")
async def get_video_interview_status(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get the status of a video interview with helpful status messages
    """
    video_interview = db.query(DBVideoInterview).filter(
        DBVideoInterview.session_id == session_id
    ).first()
    
    if not video_interview:
        raise HTTPException(status_code=404, detail="Video interview session not found")
    
    # Verify user ownership if authenticated
    if current_user and video_interview.user_id != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to view this session")
    
    # Build response with status information
    response = {
        "session_id": video_interview.session_id,
        "user_id": video_interview.user_id,
        "position": video_interview.position,
        "question_text": video_interview.question_text,
        "status": video_interview.status,
        "video_path": video_interview.video_path,
        "created_at": video_interview.created_at,
        "has_results": video_interview.status == "completed"
    }
    
    # Add status-specific information
    if video_interview.status == "pending":
        response["next_step"] = "Upload video file"
        response["can_upload"] = True
    elif video_interview.status == "processing":
        response["next_step"] = "Wait for processing to complete"
        response["can_upload"] = False
    elif video_interview.status == "completed":
        response["next_step"] = "View results"
        response["can_upload"] = False
        response["has_feedback"] = bool(video_interview.feedback)
        response["has_transcript"] = bool(video_interview.transcript)
    elif video_interview.status == "failed":
        response["next_step"] = "Check error and retry"
        response["can_upload"] = True
        response["error"] = video_interview.feedback
    
    return response


@router.get("/results/{session_id}")
async def get_video_interview_results(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get detailed results of a video interview (works for all statuses)
    Returns partial results if still processing, or error message if failed
    """
    video_interview = db.query(DBVideoInterview).filter(
        DBVideoInterview.session_id == session_id
    ).first()
    
    if not video_interview:
        raise HTTPException(status_code=404, detail="Video interview session not found")
    
    # Verify user ownership if authenticated
    if current_user and video_interview.user_id != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to view this session")
    
    # Return results regardless of status
    result = {
        "session_id": video_interview.session_id,
        "question": video_interview.question_text,
        "position": video_interview.position,
        "status": video_interview.status,
        "transcript": video_interview.transcript or "",
        "feedback": video_interview.feedback or "",
        "scores": video_interview.scores or {},
        "analysis": video_interview.analysis or {},
        "created_at": video_interview.created_at
    }
    
    # Add status-specific messages
    if video_interview.status == "processing":
        result["message"] = "Video is still being processed. Results will be available soon."
    elif video_interview.status == "pending":
        result["message"] = "Video upload is pending. Please upload the video file."
    elif video_interview.status == "failed":
        result["message"] = "Video processing failed. Please check the feedback for error details."
    elif video_interview.status == "completed":
        result["message"] = "Video interview completed successfully."
    
    return result


@router.get("/user/history")
async def get_user_video_interview_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all video interview sessions for the current user
    """
    video_interviews = db.query(DBVideoInterview).filter(
        DBVideoInterview.user_id == current_user.username
    ).order_by(DBVideoInterview.created_at.desc()).all()
    
    return {
        "total": len(video_interviews),
        "interviews": [
            {
                "session_id": vi.session_id,
                "position": vi.position,
                "question": vi.question_text,
                "status": vi.status,
                "created_at": vi.created_at,
                "overall_score": vi.scores.get("overall_score") if vi.scores else None
            }
            for vi in video_interviews
        ]
    }


@router.delete("/delete/{session_id}")
async def delete_video_interview(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a video interview session and its associated files
    """
    video_interview = db.query(DBVideoInterview).filter(
        DBVideoInterview.session_id == session_id
    ).first()
    
    if not video_interview:
        raise HTTPException(status_code=404, detail="Video interview session not found")
    
    # Verify user ownership
    if video_interview.user_id != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to delete this session")
    
    # Delete video file if exists
    if video_interview.video_path and os.path.exists(video_interview.video_path):
        try:
            os.remove(video_interview.video_path)
        except Exception as e:
            print(f"Error deleting video file: {e}")
    
    # Delete database record
    db.delete(video_interview)
    db.commit()
    
    return {"message": "Video interview deleted successfully"}
