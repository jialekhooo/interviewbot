# Video Interview Feature Documentation

## Overview
The Video Interview feature allows users to record video responses to interview questions and receive AI-powered feedback and analysis.

## Features

### Frontend (`VideoInterview.jsx`)
- **Webcam Access**: Enables user's camera for video recording
- **Video Recording**: Records video responses using MediaRecorder API
- **Real-time Preview**: Shows live camera feed during recording
- **Upload Progress**: Displays upload progress bar
- **AI Analysis Results**: Shows detailed feedback, scores, and transcript

### Backend Components

#### 1. Database Model (`app/models/video_interview.py`)
- `DBVideoInterview`: Stores video interview sessions
  - session_id, user_id, position, question_text
  - video_path, video_duration, transcript
  - analysis, feedback, scores
  - status tracking (pending, processing, completed, failed)

#### 2. API Endpoints (`app/routers/video_interview.py`)

**POST `/api/video-interview/create`**
- Creates a new video interview session
- Body: `{ user_id, position, question_text }`
- Returns: session details with session_id

**POST `/api/video-interview/upload/{session_id}`**
- Uploads video file for analysis
- Accepts: multipart/form-data with video file
- Triggers background processing

**GET `/api/video-interview/status/{session_id}`**
- Checks processing status
- Returns: current status and available results

**GET `/api/video-interview/results/{session_id}`**
- Retrieves complete analysis results
- Returns: transcript, feedback, scores, analysis

**GET `/api/video-interview/user/history`**
- Gets all video interviews for current user
- Returns: list of past interviews with scores

**DELETE `/api/video-interview/delete/{session_id}`**
- Deletes video interview and associated files

#### 3. Video Analysis Service (`app/services/video_analysis_service.py`)

**VideoAnalysisService**
- `extract_audio_from_video()`: Extracts audio using ffmpeg
- `transcribe_audio()`: Transcribes using OpenAI Whisper API
- `analyze_interview_response()`: Analyzes using GPT-4
- `analyze_video_interview()`: Complete pipeline

**Analysis Output:**
```json
{
  "transcript": "Full text transcript...",
  "feedback": "Detailed feedback text...",
  "scores": {
    "content_quality": 8,
    "clarity": 7,
    "confidence": 8,
    "relevance": 9,
    "structure": 7,
    "overall_score": 7.8
  },
  "analysis": {
    "strengths": ["..."],
    "areas_for_improvement": ["..."],
    "specific_suggestions": ["..."],
    "communication_style": "..."
  }
}
```

## Setup Instructions

### Prerequisites
1. **FFmpeg**: Required for audio extraction
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   ```

2. **OpenAI API Key**: Set in `.env` file
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Backend Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations (database tables will be created automatically):
   ```bash
   python -m app.main
   ```

3. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

## Usage Flow

1. **Setup Interview**
   - User selects or enters a position
   - User selects or enters an interview question

2. **Record Video**
   - Click "Start Camera" to enable webcam
   - Click "Start Recording" to begin recording
   - Answer the interview question
   - Click "Stop Recording" when finished

3. **Upload & Analyze**
   - Click "Upload & Analyze"
   - Video is uploaded with progress indicator
   - Backend processes video in background

4. **View Results**
   - Transcript of spoken response
   - Overall feedback and assessment
   - Detailed scores (content, clarity, confidence, etc.)
   - Strengths and areas for improvement
   - Specific suggestions for enhancement

## API Integration

### Creating a Session
```javascript
const response = await api.post('/api/video-interview/create', {
  user_id: 'username',
  position: 'Software Engineer',
  question_text: 'Tell me about yourself.'
});
const sessionId = response.data.session_id;
```

### Uploading Video
```javascript
const formData = new FormData();
formData.append('video', videoBlob, 'interview.webm');

await api.post(`/api/video-interview/upload/${sessionId}`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
  onUploadProgress: (e) => {
    const percent = Math.round((e.loaded * 100) / e.total);
    console.log(`Upload progress: ${percent}%`);
  }
});
```

### Polling for Results
```javascript
const checkStatus = async () => {
  const response = await api.get(`/api/video-interview/status/${sessionId}`);
  if (response.data.status === 'completed') {
    const results = await api.get(`/api/video-interview/results/${sessionId}`);
    console.log(results.data);
  }
};
```

## File Storage
- Videos are stored in: `static/video_interviews/`
- Filename format: `{session_id}.{extension}`
- Audio files are temporary and deleted after transcription

## Testing Mode
The system includes a `FakeVideoAnalysisService` for testing without OpenAI API:
- Returns mock transcript, feedback, and scores
- Useful for development and testing
- Switch to real service by uncommenting in `video_analysis_service.py`

## Security Considerations
- User authentication required for all endpoints
- Users can only access their own video interviews
- Video files are stored securely on server
- File type validation on upload

## Browser Compatibility
- Requires browser support for:
  - MediaRecorder API
  - getUserMedia API
  - WebRTC
- Tested on: Chrome, Firefox, Safari, Edge (latest versions)

## Troubleshooting

### Camera Not Working
- Check browser permissions for camera/microphone
- Ensure HTTPS connection (required for getUserMedia)
- Try different browser

### Upload Fails
- Check file size limits
- Verify backend is running
- Check network connection

### Analysis Takes Too Long
- Normal processing time: 30-60 seconds
- Depends on video length and API response time
- Check OpenAI API status if issues persist

## Future Enhancements
- Support for multiple video formats
- Real-time emotion detection during recording
- Body language analysis
- Comparison with previous attempts
- Practice mode with instant feedback
- Integration with interview scheduling
