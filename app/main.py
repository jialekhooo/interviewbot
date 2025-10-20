from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.models.auth import DBUser
from app.models.interview import DBInterviewSession
from app.models.resume import DBResume
from pydantic import BaseModel
from prompt.generate_prompt import generate_interview_prompt_text
from openai import OpenAI
import os
import json
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
from app.routers import interview, auth, guidance, mock, improvement, live_streaming, resume, interview_nodb

# app.include_router(interview.router, prefix="/api/interview", tags=["interview"])
app.include_router(interview_nodb.router, prefix="/api/interview", tags=["interview"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
# app.include_router(auth.router, tags=["authentication"])
# app.include_router(guidance.router, prefix="/api/guidance", tags=["guidance"])
# app.include_router(mock.router, prefix="/api/mock", tags=["mock_interview"])
# app.include_router(improvement.router, prefix="/api/improvement", tags=["resume_improvement"])
app.include_router(live_streaming.router, prefix="/api/live_streaming", tags=["live_streaming"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])

# Optionally enable resume router (requires heavy deps). Set ENABLE_RESUME_ROUTER=true to include.
if os.getenv("ENABLE_RESUME_ROUTER", "false").lower() in ("1", "true", "yes", "on"):
    from app.routers import resume
    app.include_router(resume.router, prefix="/api/resume", tags=["resume"])

class QuestionRequest(BaseModel):
    resume: str | None = None
    job_description: str | None = None
    past_conversations: str | None = None
    position: str | None = None
    difficulty: str | None = "Medium"
    question_type: str | None = "General"

@app.post("/questions")
async def generate_question(req: QuestionRequest):
    prompt_text = generate_interview_prompt_text(
        resume=req.resume,
        job_description=req.job_description,
        past_conversations=req.past_conversations,
        position=req.position,
        difficulty=req.difficulty,
        question_type=req.question_type
    )

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt_text}]
    )

    # Parse JSON output from the model
    question_data = json.loads(response.choices[0].message.content.strip())
    return question_data

"""
Temporarily disabled routers left commented to keep the app lightweight.
Enable only Bubble integration endpoints for Bubble.io frontend.
"""
from app.routers import bubble_integration
app.include_router(bubble_integration.router, prefix="/api/bubble", tags=["bubble_integration"]) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

