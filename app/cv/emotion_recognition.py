from deepface import DeepFace

def detect_emotions(frame):
    try:
        analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        return {
            "dominant_emotion": analysis['dominant_emotion'],
            "emotion_confidence": analysis['emotion']['score']
        }
    except Exception as e:
        return {"error": str(e)}
