import os
import shutil
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import status
from fastapi import Body
from typing import Optional

router = APIRouter()

@router.get("/health")
async def stt_health():
    """Health check for STT service"""
    return {
        "service": "stt",
        "endpoints": ["/transcribe", "/transcribe_api"]
    }

@router.post("/transcribe")
async def transcribe_audio_file(file: UploadFile):
    """
    Transcribe an audio file using OpenAI Whisper API.
    Now uses cloud API instead of local model to save memory.
    Supports MP3, WAV, M4A, and other common audio formats.
    """
    from fastapi.responses import JSONResponse
    from openai import OpenAI
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Check for allowed file types (expanded format support)
    filename = (file.filename or "").lower()
    supported_formats = (".mp3", ".wav", ".m4a", ".webm", ".mp4", ".mpeg", ".mpga", ".oga", ".ogg")
    if not filename.endswith(supported_formats):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported: {', '.join(supported_formats)}"
        )

    # Save uploaded file to a temp location
    fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(filename)[1])
    os.close(fd)

    try:
        with open(temp_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
        
        # Transcribe using OpenAI Whisper API
        with open(temp_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="json",
                language="en"  # Force English language
            )
        
        return {"text": result.text, "engine": "whisper-1"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as cleanup_err:
                print(f"Warning: failed to delete temp file: {cleanup_err}")


# stt_app.py
import os, uuid, shutil, tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "whisper-1"  # OpenAI Whisper model for transcription

@router.post("/transcribe_api")
async def stt(file: UploadFile = File(...)):
    """
    Transcribe audio file using OpenAI Whisper API.
    Supports MP3, WAV, M4A, and other common audio formats.
    """
    name = (file.filename or "").lower()
    # Expand supported formats
    supported_formats = (".mp3", ".wav", ".m4a", ".webm", ".mp4", ".mpeg", ".mpga", ".oga", ".ogg")
    if not name.endswith(supported_formats):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported: {', '.join(supported_formats)}"
        )
    
    fd = None
    temp_path = None
    try:
        suffix = os.path.splitext(name)[1] or ".bin"
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        with open(temp_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
        await file.close()

        with open(temp_path, "rb") as fh:
            # Use OpenAI Whisper for transcription
            result = client.audio.transcriptions.create(
                model=MODEL,
                file=fh,
                response_format="json",
                language="en"  # Force English language
            )
        return JSONResponse({"text": result.text, "engine": "whisper-1"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
