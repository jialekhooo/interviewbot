import os
import shutil
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import status
from fastapi import Body
from typing import Optional

from app.routers.interview_nodb import submit_answer
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
    Transcribe an audio file (e.g. MP3 or WAV) using Whisper.
    Returns {"text": "..."}
    """

    # Check for allowed file types
    filename = (file.filename or "").lower()
    if not (filename.endswith(".mp3") or filename.endswith(".wav")):
        raise HTTPException(status_code=400, detail="Only MP3 and WAV files are supported")

    # Save uploaded file to a temp location
    fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(filename)[1])
    os.close(fd)

    try:
        with open(temp_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)

        # Transcribe using Whisper
        result = transcribe_audio(temp_path)

        # return submit_answer(result)
        return {"text": result, "engine": "whisper"}

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

ALLOWED_MIME = {
    "audio/mpeg", "audio/mp3", "audio/mp4", "audio/mpga", "audio/m4a",
    "audio/wav", "audio/webm", "video/mp4", "video/webm"
}

MODEL = "gpt-4o-mini-transcribe"  # or "gpt-4o-transcribe" when available

@router.post("/transcribe_api")
async def stt(file: UploadFile = File(...), translate: bool = False):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    tmpdir = tempfile.mkdtemp()
    try:
        # Save to a temp file
        ext = os.path.splitext(file.filename or "")[1] or ".bin"
        path = os.path.join(tmpdir, f"{uuid.uuid4()}{ext}")
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # OpenAI Audio Transcriptions
        with open(path, "rb") as fh:
            if translate:
                # translate+transcribe to English
                result = client.audio.transcriptions.create(
                    model=MODEL, file=fh, response_format="json", translate=True
                )
            else:
                result = client.audio.transcriptions.create(
                    model=MODEL, file=fh, response_format="json"
                )

        # result typically includes text and possibly segments depending on model
        return JSONResponse({"text": result.text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
