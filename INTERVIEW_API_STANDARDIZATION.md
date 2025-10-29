# Interview API Standardization

## Overview
All interview endpoints have been standardized to only require three parameters:
1. **position** (string, required) - The job position
2. **job_description** (string, optional) - Job description as text
3. **file** (file, required) - Resume file (PDF/DOCX)

## Changes Made

### Backend Changes

#### 1. Database Model (`app/models/interview.py`)
- ✅ Added `job_description` field to `DBInterviewSession` model
- Stores job description in the session for use in subsequent questions

#### 2. Interview Router (`app/routers/interview.py`)
- ✅ `/start` endpoint now stores `job_description` in the session
- ✅ `/answer` endpoint retrieves `job_description` from the session instead of hardcoding empty string
- No longer requires `jd_file` parameter

#### 3. Interview No-DB Router (`app/routers/interview_nodb.py`)
- ✅ Removed `jd_file` parameter from all endpoints:
  - `/start`
  - `/answer`
  - `/feedback`
- ✅ Uses `job_description` string directly from form data

### Frontend Changes

#### 1. Interview.jsx (`frontend/src/pages/Interview.jsx`)
**Removed:**
- `jdFile` state variable
- Job description file upload input
- File validation for job description

**Added:**
- `position` state variable (text input)
- `jobDescription` state variable (textarea)
- Text inputs for position and job description

**Updated:**
- Form validation now checks for `position.trim()` instead of `jdFile`
- API calls send `position` and `jobDescription` as strings
- Reset function clears `position` and `jobDescription` instead of `jdFile`

#### 2. SpeechInterview.jsx (`frontend/src/pages/SpeechInterview.jsx`)
**Removed:**
- `jobDescriptionFile` state variable
- `handleJobDescriptionChange` function
- Job description file upload input

**Added:**
- `position` state variable (text input, required)
- `jobDescription` state variable (textarea, optional)
- Text inputs for position and job description

**Updated:**
- Form validation checks for `position.trim()` instead of `jobDescriptionFile`
- API calls send `position` and `jobDescription` as strings
- Default position changed from "Software Engineer" to empty string (user must enter)

## API Endpoints Summary

### `/api/interview/start` (POST)
**Parameters:**
- `position` (Form, string, required) - Job position
- `job_description` (Form, string, optional) - Job description text
- `file` (File, required) - Resume file (PDF/DOCX)

**Response:**
```json
{
  "session_id": "uuid",
  "question_id": "uuid",
  "question": "First interview question",
  "status": "in_progress"
}
```

### `/api/interview/answer` (POST)
**Parameters:**
- `question_id` (Form, string, required) - Current question ID
- `response_text` (Form, string, required) - User's answer
- `file` (File, required) - Resume file (for context)

**Response (Next Question):**
```json
{
  "type": "next_question",
  "next_question": {
    "id": "uuid",
    "text": "Next question"
  }
}
```

**Response (Interview Complete):**
```json
{
  "type": "interview_complete",
  "feedback": "Overall feedback text",
  "summary": {
    "questions_answered": 5,
    "session_id": "uuid",
    "end_time": "ISO timestamp"
  }
}
```

### `/api/interview_nodb/start` (POST)
**Parameters:**
- `position` (Form, string, required)
- `job_description` (Form, string, optional)
- `file` (File, required)

### `/api/interview_nodb/answer` (POST)
**Parameters:**
- `position` (Form, string, required)
- `job_description` (Form, string, optional)
- `past_questions` (Form, string, required) - Delimited by "||,"
- `past_answers` (Form, string, required) - Delimited by "||,"
- `answer` (Form, string, required)
- `file` (File, required)

### `/api/interview_nodb/feedback` (POST)
**Parameters:**
- `position` (Form, string, required)
- `job_description` (Form, string, optional)
- `past_questions` (Form, string, required)
- `past_answers` (Form, string, required)
- `file` (File, required)

## User Experience Changes

### Before:
- Users had to upload TWO files:
  1. Resume (PDF/DOCX)
  2. Job Description (PDF/DOCX/TXT/Screenshot)
- Position was auto-extracted or hardcoded

### After:
- Users provide THREE simple inputs:
  1. **Position** (text input, required) - e.g., "Software Engineer"
  2. **Job Description** (textarea, optional) - Paste job description text
  3. **Resume** (file upload, required) - PDF/DOCX file

## Benefits

1. **Simpler UX** - No need to upload job description files or take screenshots
2. **Faster Setup** - Copy-paste job description instead of file upload
3. **More Flexible** - Users can easily edit or skip job description
4. **Consistent API** - All endpoints use the same parameter structure
5. **Better Storage** - Job description stored in database for session continuity

## Migration Notes

### Database Migration Required
The `interview_sessions` table now has a new column:
- `job_description` (String, nullable)

You may need to run a database migration or manually add this column:
```sql
ALTER TABLE interview_sessions ADD COLUMN job_description TEXT;
```

### Breaking Changes
- Frontend must now send `position` as a required parameter
- `jd_file` parameter is no longer accepted (will be ignored if sent)
- Old frontend code sending `jd_file` will need to be updated

## Testing Checklist

- [x] Backend accepts position, job_description, and file
- [x] Backend stores job_description in session
- [x] Backend uses stored job_description for subsequent questions
- [x] Frontend sends position as text input
- [x] Frontend sends job_description as textarea
- [x] Frontend validates position is not empty
- [x] Interview.jsx updated and working
- [x] SpeechInterview.jsx updated and working
- [ ] Database migration applied
- [ ] End-to-end testing completed
- [ ] Production deployment verified
