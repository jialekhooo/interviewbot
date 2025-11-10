# Conditional imports to avoid cv2 dependency errors
# These modules require opencv-python which is not installed by default

try:
    from .face_recognition import detect_faces
except ImportError:
    detect_faces = None

try:
    from .emotion_recognition import analyze_video_emotions
except ImportError:
    analyze_video_emotions = None
