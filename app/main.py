from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.models.auth import DBUser
from app.models.interview import DBInterviewSession
from app.models.resume import DBResume
from app.models.gpt_result import DBGPTResult
from app.models.post import DBPost
from pydantic import BaseModel
from openai import OpenAI
import os
import json

# Only import video interview model if feature is enabled
if os.getenv("ENABLE_VIDEO_INTERVIEW", "false").lower() in ("1", "true", "yes", "on"):
    from app.models.video_interview import DBVideoInterview
app = FastAPI(title="Interview Chatbot API",
              description="API for the Interview Preparation Chatbot",
              version="1.0.0")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base.metadata.drop_all(bind=engine)  # Drops the tables
Base.metadata.create_all(bind=engine)  # Recreates the tables
@app.get("/")
async def root():
    return {"message": "Welcome to the Interview Chatbot API"}

@app.get("/health")
async def health():
    """Health check endpoint for Render/monitoring."""
    return {"status": "ok", "version": "1.0.1"}

# Import and include routers (avoid importing heavy resume router by default)
from app.routers import interview, auth, guidance, mock, interview_nodb, stt, posts, cv, resume_builder, resume

# Use interview_nodb router instead of interview
app.include_router(interview_nodb.router, prefix="/api/interview", tags=["interview"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(guidance.router, prefix="/api/guidance", tags=["guidance"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(mock.router, prefix="/api/mock", tags=["mock_interview"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(stt.router, prefix="/api/stt", tags=["stt"])
app.include_router(cv.router, prefix="/api/cv", tags=["cv"])
app.include_router(resume_builder.router, prefix="/api/resume-builder", tags=["resume_builder"])

# Include live_streaming only when explicitly enabled (opencv dependency)
if os.getenv("ENABLE_LIVE_STREAMING", "true").lower() in ("1", "true", "yes", "on"):
    from app.routers import live_streaming
    app.include_router(live_streaming.router, prefix="/api/live_streaming", tags=["live_streaming"])

# Enable resume improvement router (disabled by default - requires PyPDF2)
# Set ENABLE_IMPROVEMENT=true to enable
if os.getenv("ENABLE_IMPROVEMENT", "false").lower() in ("1", "true", "yes", "on"):
    from app.routers import improvement
    app.include_router(improvement.router, prefix="/api/improvement", tags=["resume_improvement"])

# Enable resume router (disabled by default - requires PyPDF2)
# Set ENABLE_RESUME_ROUTER=true to enable
if os.getenv("ENABLE_RESUME_ROUTER", "false").lower() in ("1", "true", "yes", "on"):
    from app.routers import resume
    app.include_router(resume.router, prefix="/api/resume", tags=["resume"])

# Enable video interview router (disabled by default in production)
# Set ENABLE_VIDEO_INTERVIEW=true to enable (requires ffmpeg and additional dependencies)
if os.getenv("ENABLE_VIDEO_INTERVIEW", "false").lower() in ("1", "true", "yes", "on"):
    from app.routers import video_interview
    app.include_router(video_interview.router, prefix="/api/video-interview", tags=["video_interview"])

"""
Temporarily disabled routers left commented to keep the app lightweight.
Enable only Bubble integration endpoints for Bubble.io frontend.
"""
from app.routers import bubble_integration
app.include_router(bubble_integration.router, prefix="/api/bubble", tags=["bubble_integration"]) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

