# ✅ Bubble.io Integration - READY TO CONNECT

Your backend is **100% ready** for Bubble.io integration!

## 🔗 Backend URL
```
https://interviewbot-rjsi.onrender.com
```

---

## 📋 Available API Endpoints for Bubble.io

### 1️⃣ Resume Builder - PDF Export
**Endpoint:** `POST /api/resume-builder/generate-pdf`

**Request Body (JSON):**
```json
{
  "name": "John Doe",
  "course": "Computer Science",
  "education_background": "BS Computer Science, XYZ University, 2020-2024",
  "skills": "Python, JavaScript, React, SQL",
  "internship_experience": "Software Intern at ABC Company",
  "additional_info": "Dean's List, Projects",
  "user_id": "optional"
}
```

**Response:** PDF file (binary)
- Content-Type: `application/pdf`
- Filename: `{Name}_Resume.pdf`

---

### 2️⃣ Resume Builder - DOCX Export
**Endpoint:** `POST /api/resume-builder/generate-docx`

**Request Body:** Same as PDF endpoint

**Response:** DOCX file (binary)
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Filename: `{Name}_Resume.docx`

---

### 3️⃣ Resume Builder - Text/Markdown (Bubble Integration)
**Endpoint:** `POST /api/bubble/resume/generate`

**Request Body (JSON):**
```json
{
  "name": "John Doe",
  "major": "Computer Science",
  "education_background": "BS CS, XYZ University",
  "skills": "Python, JavaScript, React",
  "internship_experience": "Software Intern at ABC",
  "additional": "Dean's List",
  "user_id": "optional"
}
```

**Response (JSON):**
```json
{
  "success": true,
  "message": "Resume generated successfully",
  "data": {
    "resume_text": "# John Doe\n\n## Education...",
    "format": "markdown",
    "result_id": 123,
    "created_at": "2024-11-01T03:00:00"
  }
}
```

---

### 4️⃣ Interview - Start Session
**Endpoint:** `POST /api/bubble/interview/start`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `user_id` (text) - User identifier
- `position` (text) - Job position (e.g., "Software Engineer")
- `job_description` (text, optional) - Job description
- `interview_mode` (text) - "text" or "realistic"
- `resume_file` (file) - PDF or DOCX resume

**Response (JSON):**
```json
{
  "success": true,
  "message": "Interview started successfully",
  "data": {
    "session_id": "uuid",
    "question_id": "uuid",
    "question": "Tell me about yourself...",
    "interview_mode": "text",
    "position": "Software Engineer",
    "question_number": 1,
    "max_questions": 5
  }
}
```

---

### 5️⃣ Interview - Submit Answer
**Endpoint:** `POST /api/bubble/interview/submit-answer`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `session_id` (text) - From start response
- `question_id` (text) - Current question ID
- `answer_text` (text) - User's answer
- `position` (text) - Job position
- `job_description` (text, optional)
- `past_questions` (text) - Questions joined by "||,"
- `past_answers` (text) - Answers joined by "||,"
- `resume_file` (file) - Same resume file

**Optional (for realistic mode):**
- `words_per_minute` (number)
- `filler_words_count` (number)
- `confidence_score` (number, 0-100)
- `eye_contact_score` (number, 0-100)
- `engagement_score` (number, 0-100)

**Response - In Progress (JSON):**
```json
{
  "success": true,
  "message": "Answer received, next question generated",
  "data": {
    "status": "in_progress",
    "next_question_id": "uuid",
    "next_question": "Next question text",
    "sample_answer": "Sample answer...",
    "question_number": 2,
    "max_questions": 5
  }
}
```

**Response - Completed (JSON):**
```json
{
  "success": true,
  "message": "Interview completed",
  "data": {
    "status": "completed",
    "final_feedback": "Overall feedback...",
    "strengths": ["Strength 1", "Strength 2"],
    "areas_for_improvement": ["Area 1", "Area 2"],
    "overall_assessment": "Assessment text",
    "sample_answers": ["Answer 1", "Answer 2"],
    "performance_summary": {
      "speech_analysis": {
        "words_per_minute": 150,
        "filler_words": 3,
        "confidence": 85
      },
      "visual_analysis": {
        "eye_contact": 90,
        "engagement": 88
      }
    },
    "questions_answered": 5
  }
}
```

---

### 6️⃣ Interview Templates
**Endpoint:** `GET /api/bubble/interview/templates`

**Response (JSON):**
```json
{
  "success": true,
  "message": "Interview templates retrieved",
  "data": {
    "templates": {
      "Software Engineer": ["Question 1", "Question 2", ...],
      "Product Manager": ["Question 1", "Question 2", ...],
      "Data Scientist": ["Question 1", "Question 2", ...],
      "General": ["Question 1", "Question 2", ...]
    }
  }
}
```

---

### 7️⃣ Resume Analysis
**Endpoint:** `POST /api/bubble/resume/analyze`

**Request Body (JSON):**
```json
{
  "resume_text": "Full resume text...",
  "target_role": "Software Engineer"
}
```

**Response (JSON):**
```json
{
  "success": true,
  "message": "Resume analyzed successfully",
  "data": {
    "analysis": "Analysis text...",
    "score": 7.5,
    "target_role": "Software Engineer"
  }
}
```

---

### 8️⃣ Answer Guidance
**Endpoint:** `POST /api/bubble/guidance/improve`

**Request Body (JSON):**
```json
{
  "question": "Tell me about yourself",
  "user_answer": "I am a software engineer...",
  "context": "Optional context"
}
```

**Response (JSON):**
```json
{
  "success": true,
  "message": "Guidance generated successfully",
  "data": {
    "guidance": "Improvement suggestions...",
    "question": "Tell me about yourself",
    "improved_answer": "See guidance for improvements"
  }
}
```

---

### 9️⃣ Save Results
**Endpoint:** `POST /api/bubble/results/save`

**Request Body (JSON):**
```json
{
  "category": "resume",
  "output_text": "Generated content...",
  "user_id": "optional",
  "input_data": {"key": "value"}
}
```

**Response (JSON):**
```json
{
  "success": true,
  "message": "Saved",
  "data": {
    "result_id": 123,
    "created_at": "2024-11-01T03:00:00"
  }
}
```

---

### 🔟 List Results
**Endpoint:** `POST /api/bubble/results/list`

**Request Body (JSON):**
```json
{
  "user_id": "optional",
  "category": "optional",
  "limit": 20,
  "offset": 0
}
```

**Response (JSON):**
```json
{
  "success": true,
  "message": "Results fetched",
  "data": {
    "items": [
      {
        "id": 123,
        "user_id": "user123",
        "category": "resume",
        "output_text": "Content...",
        "input_data": {},
        "created_at": "2024-11-01T03:00:00"
      }
    ],
    "count": 1
  }
}
```

---

### 1️⃣1️⃣ Get Single Result
**Endpoint:** `GET /api/bubble/results/{result_id}`

**Response (JSON):**
```json
{
  "success": true,
  "message": "Result fetched",
  "data": {
    "id": 123,
    "user_id": "user123",
    "category": "resume",
    "output_text": "Content...",
    "input_data": {},
    "created_at": "2024-11-01T03:00:00"
  }
}
```

---

### 1️⃣2️⃣ Health Check
**Endpoint:** `GET /api/bubble/health`

**Response (JSON):**
```json
{
  "success": true,
  "message": "Bubble.io integration is healthy",
  "data": {
    "status": "ok",
    "timestamp": "2024-11-01T03:00:00",
    "available_modes": ["text", "realistic"],
    "endpoints": [...]
  }
}
```

---

## ✅ Backend Configuration Status

### CORS - ✅ READY
```javascript
allow_origins: ["*"]
allow_credentials: true
allow_methods: ["*"]
allow_headers: ["*"]
```
✅ Your Bubble.io app can call any endpoint

### Authentication - ✅ OPTIONAL
- API key authentication available via `BUBBLE_API_KEY` env var
- Currently **public** (no key required)
- To enable: Set `BUBBLE_API_KEY` in Render dashboard

### File Uploads - ✅ READY
- Supports PDF and DOCX resume uploads
- Uses `multipart/form-data` for interview endpoints
- File parsing included (`PyPDF2`, `python-docx`)

### Dependencies - ✅ READY
```
✅ reportlab - PDF generation
✅ python-docx - DOCX generation
✅ PyPDF2 - PDF parsing
✅ openai - AI features
✅ fastapi - API framework
✅ sqlalchemy - Database
```

### Database - ✅ READY
- SQLite (auto-created on startup)
- Stores interview results, resumes, user data
- ⚠️ Note: Ephemeral on Render free tier (resets on restart)

---

## 🚀 Quick Start in Bubble.io

### Step 1: Add API Connector
1. Go to **Plugins** → Add **API Connector**

### Step 2: Add API Calls

#### For Resume PDF Export:
- **Name:** `Generate Resume PDF`
- **Type:** Action, Data type: File
- **Method:** POST
- **URL:** `https://interviewbot-rjsi.onrender.com/api/resume-builder/generate-pdf`
- **Body:** JSON with fields: name, course, education_background, skills, internship_experience, additional_info

#### For Resume DOCX Export:
- **Name:** `Generate Resume DOCX`
- Same as PDF but URL: `/api/resume-builder/generate-docx`

#### For Interview Start:
- **Name:** `Start Interview`
- **Type:** Action, Data type: JSON
- **Method:** POST
- **URL:** `https://interviewbot-rjsi.onrender.com/api/bubble/interview/start`
- **Body type:** Form-data
- **Fields:** user_id, position, job_description, interview_mode, resume_file

#### For Interview Submit:
- **Name:** `Submit Answer`
- **Type:** Action, Data type: JSON
- **Method:** POST
- **URL:** `https://interviewbot-rjsi.onrender.com/api/bubble/interview/submit-answer`
- **Body type:** Form-data
- **Fields:** session_id, question_id, answer_text, position, past_questions, past_answers, resume_file

### Step 3: Create Workflows
1. **Resume Builder:**
   - Input fields → Button click → API call → Download file

2. **Interview:**
   - Upload resume → Start interview → Display question
   - Answer input → Submit answer → Show next question or feedback

### Step 4: Test
- Use the health check endpoint to verify connection
- Test with sample data
- Check Render logs for any errors

---

## 🧪 Testing Endpoints

### Test Resume PDF (cURL):
```bash
curl -X POST "https://interviewbot-rjsi.onrender.com/api/resume-builder/generate-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "course": "Computer Science",
    "education_background": "BS CS, Test University",
    "skills": "Python, JavaScript",
    "internship_experience": "Software Intern",
    "additional_info": "Projects"
  }' \
  --output test.pdf
```

### Test Health Check:
```bash
curl https://interviewbot-rjsi.onrender.com/api/bubble/health
```

### Test Interview Start (requires file):
```bash
curl -X POST "https://interviewbot-rjsi.onrender.com/api/bubble/interview/start" \
  -F "user_id=test123" \
  -F "position=Software Engineer" \
  -F "interview_mode=text" \
  -F "resume_file=@/path/to/resume.pdf"
```

---

## 📊 API Response Format

All Bubble.io endpoints return consistent format:
```json
{
  "success": true/false,
  "message": "Human-readable message",
  "data": {
    // Endpoint-specific data
  }
}
```

**Success:** `success: true`
**Error:** `success: false` with error message

---

## 🔐 Security (Optional)

To enable API key authentication:

1. Set environment variable in Render:
   ```
   BUBBLE_API_KEY=your-secret-key
   ```

2. In Bubble.io API Connector, add header:
   ```
   X-API-Key: your-secret-key
   ```
   OR
   ```
   Authorization: Bearer your-secret-key
   ```

---

## 📝 Important Notes

### File Size Limits
- Resume files: Recommended < 10MB
- Render free tier has request timeout limits

### Cold Starts
- Render free tier sleeps after 15 min inactivity
- First request after sleep takes ~30 seconds
- Subsequent requests are fast

### Database
- SQLite database resets on Render restart (free tier)
- For production: Upgrade to persistent disk or use PostgreSQL

### Rate Limits
- OpenAI API has rate limits
- Monitor usage in OpenAI dashboard

---

## ✅ Checklist

- [x] CORS configured for Bubble.io
- [x] All endpoints documented
- [x] PDF/DOCX export working
- [x] Interview flow implemented
- [x] Resume generation working
- [x] File upload support ready
- [x] Database configured
- [x] Health check endpoint
- [x] Error handling in place
- [x] Consistent response format

---

## 🎉 You're Ready!

Your backend is **production-ready** for Bubble.io integration!

**Next Steps:**
1. Deploy to Render (if not already deployed)
2. Configure API calls in Bubble.io
3. Build your UI workflows
4. Test end-to-end
5. Launch! 🚀

**Need Help?**
- API Docs: `https://interviewbot-rjsi.onrender.com/docs`
- Health Check: `https://interviewbot-rjsi.onrender.com/api/bubble/health`
- Full Guide: See `BUBBLE_RESUME_EXPORT_GUIDE.md`
