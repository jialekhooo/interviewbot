import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.cv.emotion_recognition import analyze_video_emotions
router = APIRouter()

@router.get("/health")
async def cv_health():
    return {
        "service": "cv"
    }

@router.post("/analyze_video/")
async def analyze_video(file: UploadFile = File(...)):
    """
    Endpoint: POST /analyze_video/
    Receives a video file, analyzes emotions, and returns a summary.
    """
    try:
        # Save uploaded video to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Analyze video emotions
        results = analyze_video_emotions(tmp_path)

        return JSONResponse(content={
            "engine": "deepface",
            "results": results
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
