import whisper

# Load the Whisper model once
model = whisper.load_model("small")

def transcribe_audio(file_path):
    """
    Transcribe audio file to text using Whisper
    """
    result = model.transcribe(file_path)
    return result['text']
