import os
import shutil
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import status
from fastapi import Body
from typing import Optional
from app.stt.speech_to_text import transcribe_audio
router = APIRouter()

@router.get("/health")
async def stt_health():
    return {
        "service": "stt"
    }

@router.post("/transcribe")
async def transcribe_audio_file(file: UploadFile):
    """
    Transcribe a WAV audio file (mono, 16-bit PCM) into text using Vosk.
    Returns {"text": "..."}
    """
    # Check if it's a WAV file
    content_type = (file.content_type or "").lower()
    filename = (file.filename or "").lower()
    if not (content_type in ("audio/wav", "audio/x-wav", "audio/wave") or filename.endswith(".wav")):
        raise HTTPException(status_code=400, detail="Only WAV files are supported (mono, 16-bit PCM)")

    # Create a temp file manually (Windows-compatible)
    fd, tmp_file_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)  # Close the file descriptor immediately

    try:
        # Save the uploaded file content
        with open(tmp_file_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)

        # Perform transcription
        result = transcribe_audio(tmp_file_path)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"text": result, "engine": "whisper"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    finally:
        # Always clean up the temp file
        if os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except Exception as cleanup_err:
                print(f"Warning: could not delete temp file {tmp_file_path}: {cleanup_err}")
