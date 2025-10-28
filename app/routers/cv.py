import os
import shutil
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import status
from fastapi import Body
from typing import Optional

from app.routers.interview_nodb import submit_answer
from app.cv.emotion_recognition import detect_emotions
router = APIRouter()

@router.get("/health")
async def cv_health():
    return {
        "service": "cv"
    }

# @router.post("/detect_emotions")
# async def detect_emotions_endpoint(file: UploadFile = File(...)):
#
#     try:
#
#         # Transcribe using Whisper
#         result = detect_emotions(file.file.read())
#
#         # return submit_answer(result)
#         return {"text": result, "engine": "deepface"}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
