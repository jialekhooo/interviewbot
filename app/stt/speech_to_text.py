import whisper

# Load the Whisper model once
model = whisper.load_model("small")

def transcribe_audio(file_path):
    """
    Transcribe audio file to text using Whisper in ENGLISH ONLY
    """
    # ✅ FORCE ENGLISH LANGUAGE
    result = model.transcribe(file_path, language='en')
    return result['text']


# print(transcribe_audio("C:/Users/User/PycharmProjects/interviewbot/app/stt/test.wav"))