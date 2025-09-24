from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os

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

@app.get("/")
async def root():
    return {"message": "Welcome to the Interview Chatbot API"}

@app.get("/health")
async def health():
    """Health check endpoint for Render/monitoring."""
    return {"status": "ok"}

# Import and include routers
from app.routers import resume, interview, auth, guidance, mock, improvement, bubble_integration

app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(interview.router, prefix="/api/interview", tags=["interview"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(guidance.router, prefix="/api/guidance", tags=["guidance"])
app.include_router(mock.router, prefix="/api/mock", tags=["mock_interview"])
app.include_router(improvement.router, prefix="/api/improvement", tags=["resume_improvement"])
app.include_router(bubble_integration.router, prefix="/api/bubble", tags=["bubble_integration"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
