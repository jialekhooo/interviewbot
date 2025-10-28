from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from deepface import DeepFace
import cv2
import numpy as np
import tempfile
from collections import Counter

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

# cv.py
import os, subprocess, glob

def _run_ffmpeg(cmd: list):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def extract_scene_frames(video_path: str, outdir: str, scene_thresh: float = 0.4, scale_w: int = 640):
    os.makedirs(outdir, exist_ok=True)
    vf = f"select=gt(scene\\,{scene_thresh}),scale={scale_w}:-1"
    _run_ffmpeg(["ffmpeg", "-i", video_path, "-vf", vf, "-vsync", "vfr", "-frame_pts", "1",
                 os.path.join(outdir, "sc_%010d.jpg")])

def extract_uniform_frames(video_path: str, outdir: str, fps: str = "1/4", scale_w: int = 640):
    os.makedirs(outdir, exist_ok=True)
    vf = f"fps={fps},scale={scale_w}:-1"
    _run_ffmpeg(["ffmpeg", "-i", video_path, "-vf", vf, "-vsync", "vfr", "-frame_pts", "1",
                 os.path.join(outdir, "uf_%010d.jpg")])

def pick_evenly_spaced(paths, k: int):
    if len(paths) <= k:
        return paths
    idxs = [round(i*(len(paths)-1)/(k-1)) for i in range(k)]
    return [paths[i] for i in idxs]

def load_bytes(paths):
    imgs = []
    for p in paths:
        with open(p, "rb") as f:
            imgs.append(f.read())
    return imgs

def get_frames_for_scoring(video_path: str, workdir: str, max_images: int = 8,
                           scene_thresh: float = 0.4, fps: str = "1/4", scale_w: int = 640):
    sc_dir = os.path.join(workdir, "sc")
    extract_scene_frames(video_path, sc_dir, scene_thresh, scale_w)
    sc_frames = sorted(glob.glob(os.path.join(sc_dir, "*.jpg")))
    candidates = list(sc_frames)
    if len(candidates) < 4:
        uf_dir = os.path.join(workdir, "uf")
        extract_uniform_frames(video_path, uf_dir, fps, scale_w)
        candidates.extend(sorted(glob.glob(os.path.join(uf_dir, "*.jpg"))))
    if not candidates:
        return [], []
    chosen_paths = pick_evenly_spaced(sorted(candidates), max_images)
    images = load_bytes(chosen_paths)
    basenames = [os.path.basename(p) for p in chosen_paths]
    return images, basenames

