import whisper

# Lazy-load the Whisper model to avoid startup delays
_model = None

def get_model():
    """Get or load the Whisper model (lazy loading)"""
    global _model
    if _model is None:
        _model = whisper.load_model("small")
    return _model

def transcribe_audio(file_path):
    """
    Transcribe audio file to text using Whisper in ENGLISH ONLY.
    Model is loaded on first use to avoid startup delays.
    """
    model = get_model()
    # ✅ FORCE ENGLISH LANGUAGE
    result = model.transcribe(file_path, language='en')
    return result['text']


# print(transcribe_audio("C:/Users/User/PycharmProjects/interviewbot/app/stt/test.wav"))