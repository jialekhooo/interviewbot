from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from cv import detect_faces, detect_emotions
from stt import transcribe_audio
import os
import cv2
import shutil
import numpy as np
import base64
import tempfile
import soundfile as sf

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
    return {"status": "ok", "version": "1.0.1"}

# Import and include routers - minimal version for deployment
from app.routers import interview

app.include_router(interview.router, prefix="/api/interview", tags=["interview"])

def read_image(file: UploadFile):
    contents = file.file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def save_audio(file: UploadFile):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return temp_path

    @app.post("/cv/detect-face/", summary="Detect Faces in Image")
async def face_endpoint(file: UploadFile = File(...)):
    img = read_image(file)
    faces = detect_faces(img)
    return {"faces_detected": len(faces), "faces": faces.tolist()}

@app.post("/cv/detect-emotion/", summary="Detect Emotions in Image")
async def emotion_endpoint(file: UploadFile = File(...)):
    img = read_image(file)
    result = detect_emotions(img)
    return result

    @app.websocket("/ws/speech")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time speech-to-text from microphone input.
    Audio chunks are sent in base64; transcription returned after "END".
    """
    await websocket.accept()
    audio_buffer = []

    while True:
        data = await websocket.receive_text()
        if data == "END":
            audio_data = np.array(audio_buffer, dtype=np.float32)
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(temp_file.name, audio_data, 16000)
            text = transcribe_audio(temp_file.name)
            await websocket.send_text(text)
            audio_buffer = []
        else:
            audio_chunk = np.frombuffer(base64.b64decode(data), dtype=np.float32)
            audio_buffer.extend(audio_chunk)
    return result

# Temporarily disabled to fix deployment issues
# from app.routers import resume, auth
# app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
# app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])

"""
Temporarily disabled routers left commented to keep the app lightweight.
Enable only Bubble integration endpoints for Bubble.io frontend.
"""
from app.routers import bubble_integration
app.include_router(bubble_integration.router, prefix="/api/bubble", tags=["bubble_integration"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
