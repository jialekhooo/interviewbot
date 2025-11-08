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

# endpoint.py
import os, uuid, shutil, tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.cv.emotion_recognition import get_frames_for_scoring
from app.prompts.emotion_prompt import score_professionalism_from_images

ALLOWED_MIME = {"video/mp4", "video/webm", "video/quicktime", "video/x-matroska"}
MAX_IMAGES = int(os.getenv("MAX_IMAGES", "8"))
SCENE_THRESH = float(os.getenv("SCENE_THRESH", "0.4"))
UNIFORM_FPS = os.getenv("UNIFORM_FPS", "1/4")
SCALE_W = int(os.getenv("SCALE_W", "640"))

@router.post("/analyze_cv/")
async def evaluate_cv(file: UploadFile = File(...)):
    """
    Analyze video for professionalism scoring using CV and AI.
    Requires ffmpeg to be installed on the system.
    """
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail="Unsupported video type")
    tmpdir = tempfile.mkdtemp()
    try:
        ext = os.path.splitext(file.filename or "")[1] or ".mp4"
        vpath = os.path.join(tmpdir, f"{uuid.uuid4()}{ext}")
        with open(vpath, "wb") as f:
            shutil.copyfileobj(file.file, f)

        images, frame_names = get_frames_for_scoring(
            video_path=vpath,
            workdir=tmpdir,
            max_images=MAX_IMAGES,
            scene_thresh=SCENE_THRESH,
            fps=UNIFORM_FPS,
            scale_w=SCALE_W,
        )
        if not images:
            raise HTTPException(status_code=422, detail="No frames extracted from video. Please ensure the video is valid.")

        score, details = score_professionalism_from_images(images)
        return JSONResponse({"score": score, "details": details, "frames": frame_names})
    except HTTPException:
        raise
    except RuntimeError as e:
        # FFmpeg or system errors
        raise HTTPException(status_code=500, detail=f"Video processing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
