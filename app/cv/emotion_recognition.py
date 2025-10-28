from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from deepface import DeepFace
import cv2
import numpy as np
import tempfile
from collections import Counter

app = FastAPI(title="Emotion Evaluation Service", version="1.0")

def analyze_video_emotions(video_path: str, frame_interval: int = 30):
    """
    Analyze emotions frame-by-frame in a video.
    frame_interval: number of frames to skip between analyses (higher = faster)
    """
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    emotion_results = []

    if not cap.isOpened():
        raise ValueError("Could not open video file")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Analyze every Nth frame to save time
        if frame_count % frame_interval == 0:
            try:
                analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                if isinstance(analysis, list):
                    analysis = analysis[0]
                dominant_emotion = analysis.get('dominant_emotion')
                emotion_confidences = analysis.get('emotion', {})
                emotion_results.append((dominant_emotion, emotion_confidences))
            except Exception:
                pass  # skip problematic frames

        frame_count += 1

    cap.release()

    if not emotion_results:
        return {"error": "No emotions detected"}

    # Aggregate emotions
    dominant_counts = Counter([e[0] for e in emotion_results])
    most_common_emotion, freq = dominant_counts.most_common(1)[0]

    # Average emotion confidence scores
    all_scores = {}
    for _, scores in emotion_results:
        for k, v in scores.items():
            all_scores[k] = all_scores.get(k, 0.0) + float(v)

    # Normalize
    for k in all_scores.keys():
        all_scores[k] /= len(emotion_results)

    return {
        "dominant_emotion": most_common_emotion,
        "dominant_emotion_frequency": freq,
        "average_emotions": {k: round(v, 2) for k, v in all_scores.items()},
        "frames_analyzed": len(emotion_results)
    }

