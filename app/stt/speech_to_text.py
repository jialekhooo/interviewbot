# Lazy-load the Whisper model to avoid startup delays
# Whisper import is conditional to prevent deployment failures
_model = None

def get_model():
    """
    Get or load the Whisper model (lazy loading).
    NOTE: Requires openai-whisper package to be installed.
    """
    global _model
    if _model is None:
        try:
            import whisper
        except ImportError:
            raise RuntimeError(
                "Local Whisper model requires 'openai-whisper' package. "
                "This package is not installed to save memory. "
                "Please use /transcribe_api endpoint which uses OpenAI's cloud API instead."
            )
        _model = whisper.load_model("small")
    return _model

def transcribe_audio(file_path):
    """
    Transcribe audio file to text using local Whisper model in ENGLISH ONLY.
    NOTE: Requires openai-whisper package. Use /transcribe_api for cloud-based transcription.
    Model is loaded on first use to avoid startup delays.
    """
    model = get_model()
    # ✅ FORCE ENGLISH LANGUAGE
    result = model.transcribe(file_path, language='en')
    return result['text']


# print(transcribe_audio("C:/Users/User/PycharmProjects/interviewbot/app/stt/test.wav"))