# Video Analysis API Documentation

## Endpoint: `/api/cv/analyze_cv/`

### Overview
Analyzes video interviews for professionalism scoring using computer vision and AI.

### Method
`POST`

### URL
```
https://interviewbot-rjsi.onrender.com/api/cv/analyze_cv/
```

### Swagger UI
```
https://interviewbot-rjsi.onrender.com/docs#/cv/evaluate_cv_api_cv_analyze_cv__post
```

---

## Request

### Content-Type
`multipart/form-data`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | Video file to analyze |

### Supported Video Formats
- `video/mp4` (.mp4)
- `video/webm` (.webm)
- `video/quicktime` (.mov)
- `video/x-matroska` (.mkv)

### File Size Recommendations
- **Recommended:** < 50 MB
- **Maximum:** Depends on server timeout (typically 30-60 seconds)

---

## Response

### Success Response (200 OK)

```json
{
  "score": 75,
  "details": {
    "overall": 75,
    "subscores": {
      "composure": 80,
      "eye_contact": 70,
      "smile": 75,
      "listening": 80,
      "posture": 85,
      "distractions": 60
    },
    "notes": "The candidate demonstrates good posture and composure throughout the interview. Eye contact could be improved, and there are some minor distractions visible in the background.",
    "recommendations": [
      "Maintain more consistent eye contact with the camera",
      "Remove background distractions before the interview",
      "Practice smiling naturally during responses"
    ]
  },
  "frames": [
    "sc_0000000001.jpg",
    "sc_0000000045.jpg",
    "sc_0000000089.jpg",
    "uf_0000000001.jpg",
    "uf_0000000015.jpg",
    "uf_0000000029.jpg",
    "uf_0000000043.jpg",
    "uf_0000000057.jpg"
  ]
}
```

### Error Responses

#### 415 Unsupported Media Type
```json
{
  "detail": "Unsupported video type"
}
```

#### 422 Unprocessable Entity
```json
{
  "detail": "No frames extracted from video. Please ensure the video is valid."
}
```

#### 500 Internal Server Error (FFmpeg)
```json
{
  "detail": "Video processing error: FFmpeg error: [error details]"
}
```

#### 500 Internal Server Error (General)
```json
{
  "detail": "Unexpected error: [error message]"
}
```

---

## How It Works

### 1. **Frame Extraction**
The system uses **ffmpeg** to extract key frames from the video:

- **Scene Detection:** Extracts frames when scene changes are detected (threshold: 0.4)
- **Uniform Sampling:** If < 4 scene frames, samples at 1 frame per 4 seconds
- **Maximum Frames:** 8 frames total (configurable via `MAX_IMAGES` env var)
- **Resolution:** Scaled to 640px width (configurable via `SCALE_W` env var)

### 2. **AI Analysis**
Extracted frames are analyzed using **OpenAI GPT-4o Vision** model:

- **Model:** `gpt-4o` (multimodal)
- **Evaluation Criteria:**
  - Composure (25%)
  - Eye contact (20%)
  - Smile (15%)
  - Listening cues (15%)
  - Posture (15%)
  - Distractions (10%)

### 3. **Scoring**
Returns a 0-100 score with detailed subscores and recommendations.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_IMAGES` | `8` | Maximum frames to extract |
| `SCENE_THRESH` | `0.4` | Scene change detection threshold |
| `UNIFORM_FPS` | `1/4` | Uniform sampling rate (1 frame per 4 seconds) |
| `SCALE_W` | `640` | Frame width in pixels |
| `OPENAI_VISION_MODEL` | `gpt-4o` | OpenAI vision model to use |

---

## Testing in Swagger UI

### Step 1: Navigate to Swagger UI
Open: https://interviewbot-rjsi.onrender.com/docs

### Step 2: Find the Endpoint
Scroll to **"cv"** section → `POST /api/cv/analyze_cv/`

### Step 3: Try it Out
1. Click **"Try it out"**
2. Click **"Choose File"** and select a video
3. Click **"Execute"**

### Step 4: View Response
Check the response body for:
- Overall score
- Detailed subscores
- Notes and recommendations
- Extracted frame names

---

## Testing with cURL

```bash
curl -X POST "https://interviewbot-rjsi.onrender.com/api/cv/analyze_cv/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/video.mp4"
```

---

## Testing with Python

```python
import requests

url = "https://interviewbot-rjsi.onrender.com/api/cv/analyze_cv/"

with open("interview_video.mp4", "rb") as video_file:
    files = {"file": video_file}
    response = requests.post(url, files=files)

if response.status_code == 200:
    result = response.json()
    print(f"Overall Score: {result['score']}/100")
    print(f"Notes: {result['details']['notes']}")
    print(f"Recommendations: {result['details']['recommendations']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

---

## Testing with Bubble.io

### API Connector Setup

1. **Name:** Video Analysis API
2. **Use as:** Action
3. **Data type:** JSON

### Configuration

**Method:** POST  
**URL:** `https://interviewbot-rjsi.onrender.com/api/cv/analyze_cv/`

**Body Type:** Form-data

**Parameters:**
- Key: `file`
- Type: File
- Value: `<File uploader's value>`

### Workflow

```
When Button "Analyze Video" is clicked:
  → API Call: Video Analysis API
    → file = FileUploader Video's value
  → Display result:
    → Text: "Score: [Result's score]/100"
    → Text: "Notes: [Result's details's notes]"
    → Repeating Group: [Result's details's recommendations]
```

---

## Common Issues & Solutions

### Issue 1: "FFmpeg is not installed"
**Solution:** Wait for deployment to complete. FFmpeg is now in `apt.txt`.

### Issue 2: "No frames extracted"
**Causes:**
- Video is corrupted
- Video format not supported
- Video is too short (< 1 second)

**Solution:** 
- Use MP4 format
- Ensure video is at least 5 seconds long
- Test with a different video

### Issue 3: Timeout
**Causes:**
- Video file too large
- Processing taking too long

**Solution:**
- Reduce video file size (< 50 MB recommended)
- Reduce video duration (< 2 minutes recommended)
- Compress video before upload

### Issue 4: Low scores despite good performance
**Causes:**
- Poor lighting
- Camera angle issues
- Background distractions

**Solution:**
- Ensure good lighting
- Position camera at eye level
- Use plain background
- Look directly at camera

---

## Deployment Status

✅ **Latest Deployment:** Commit `7e3ec93` - "Fix video interview CV API ffmpeg error"

**Includes:**
- ffmpeg system dependency
- Improved error handling
- Better error messages
- Model fix (gpt-4.1 → gpt-4o)

**Deployment URL:** https://interviewbot-rjsi.onrender.com

---

## Performance Metrics

**Typical Processing Time:**
- 30-second video: ~10-15 seconds
- 1-minute video: ~20-30 seconds
- 2-minute video: ~40-60 seconds

**Factors Affecting Speed:**
- Video resolution
- Video duration
- Number of scene changes
- OpenAI API response time

---

## Best Practices

### For Users
1. **Record in good lighting** - Improves AI accuracy
2. **Use plain background** - Reduces distractions score
3. **Look at camera** - Improves eye contact score
4. **Sit upright** - Improves posture score
5. **Keep video short** - Faster processing (30-60 seconds ideal)

### For Developers
1. **Set reasonable timeouts** - Video processing can take time
2. **Show loading indicators** - Processing is not instant
3. **Validate file size** - Prevent large uploads
4. **Handle errors gracefully** - Show user-friendly messages
5. **Cache results** - Avoid re-processing same video

---

## Future Enhancements

- [ ] Real-time video streaming analysis
- [ ] Emotion detection integration
- [ ] Speech analysis (combine with STT)
- [ ] Multi-person detection
- [ ] Custom scoring rubrics
- [ ] Video trimming before analysis
- [ ] Batch video processing

---

## Support

**Issues?** Check:
1. Swagger UI: https://interviewbot-rjsi.onrender.com/docs
2. Health Check: https://interviewbot-rjsi.onrender.com/api/cv/health
3. Deployment Logs: Render Dashboard

**Contact:** Check your project repository for support information.
