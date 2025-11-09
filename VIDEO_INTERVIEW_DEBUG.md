# Video Interview Results Not Showing - Debug Guide

## Problem
After video interview completes, results don't show - just "End of Interview" screen.

## Likely Causes

### 1. Bubble Workflow Not Calling Results API
**Check:** After interview ends, is there a workflow step that calls:
```
GET /api/video-interview/results/{session_id}
```

**Fix:** Add workflow:
```
When Button "End Interview" is clicked
  → API Call: Get Video Interview Results
    → session_id = State's session_id
  → Navigate to Results Page
  → Display Result's transcript, feedback, scores
```

### 2. Session ID Not Saved
**Check:** Is the session_id from `/start` being saved to a custom state?

**Fix:** When starting interview:
```
When API Call "Start Video Interview" is successful
  → Set State session_id = Result's session_id
```

### 3. Results Hidden by Condition
**Check:** Are result elements hidden when status != "completed"?

**Fix:** Show results for all statuses:
```
Text (Transcript): Result's transcript
  → Visible: Yes (always)
  → Or: When Result's status is "completed" OR "failed"
```

### 4. Processing Still Running
**Check:** Is the video still being processed?

**Fix:** Add polling workflow:
```
Every 3 seconds (while on results page):
  → API Call: Get Video Interview Status
    → session_id = State's session_id
  → If Result's status = "completed":
    → Stop polling
    → Show results
  → If Result's status = "processing":
    → Show "Processing..." message
```

---

## Test the API Directly

### 1. Get a Session ID
After completing an interview in Bubble, check the browser console or database for the `session_id`.

### 2. Test Results Endpoint
```bash
curl "https://interviewbot-rjsi.onrender.com/api/video-interview/results/{session_id}"
```

**Expected Response:**
```json
{
  "session_id": "uuid",
  "question": "Tell me about yourself...",
  "position": "Software Engineer",
  "status": "completed",
  "transcript": "I am a software engineer with...",
  "feedback": "Great answer! You demonstrated...",
  "scores": {
    "overall_score": 85,
    "communication": 90,
    "content": 80
  },
  "analysis": {...},
  "message": "Video interview completed successfully."
}
```

**If status is "processing":**
```json
{
  "status": "processing",
  "transcript": "",
  "feedback": "",
  "message": "Video is still being processed. Results will be available soon."
}
```

**If status is "failed":**
```json
{
  "status": "failed",
  "feedback": "Processing error: ...",
  "message": "Video processing failed. Please check the feedback for error details."
}
```

### 3. Check Status Endpoint
```bash
curl "https://interviewbot-rjsi.onrender.com/api/video-interview/status/{session_id}"
```

---

## Bubble.io Workflow Example

### Page: Video Interview Results

**Elements:**
- Text: Question (displays `Result's question`)
- Text: Transcript (displays `Result's transcript`)
- Text: Feedback (displays `Result's feedback`)
- Text: Score (displays `Result's scores's overall_score`)
- Group: Processing (visible when `Result's status = "processing"`)
- Group: Results (visible when `Result's status = "completed"`)
- Group: Error (visible when `Result's status = "failed"`)

**Workflows:**

1. **When Page is Loaded:**
```
API Call: Get Video Interview Results
  → session_id = Get data from URL parameter "session_id"
  → OR: session_id = Current User's last_session_id
```

2. **If Still Processing (Optional Polling):**
```
Do every 5 seconds:
  → API Call: Get Video Interview Status
  → If Result's status = "completed":
    → Refresh results
    → Stop polling
```

---

## Common Mistakes

### ❌ Mistake 1: Not Saving Session ID
```
Start Interview → Get session_id → Don't save it → Can't fetch results
```

### ✅ Fix:
```
Start Interview → Save session_id to custom state → Use it to fetch results
```

### ❌ Mistake 2: Checking Status Too Early
```
Upload video → Immediately check results → Status = "processing" → Hide results
```

### ✅ Fix:
```
Upload video → Wait or poll → Check when status = "completed" → Show results
```

### ❌ Mistake 3: Wrong Endpoint
```
Calling /status instead of /results
```

### ✅ Fix:
```
Use /results/{session_id} to get full data including transcript and feedback
```

---

## Quick Fix Checklist

- [ ] Session ID is saved after `/start` call
- [ ] Results page calls `/results/{session_id}` on load
- [ ] Result elements are visible (not hidden by conditions)
- [ ] Polling is set up if processing takes time
- [ ] Error states are handled (show error message if failed)
- [ ] API connector is configured correctly
- [ ] Session ID is passed correctly in URL or state

---

## If Results API Returns Empty Data

**Check:**
1. Is video actually uploaded? (Check `/status` endpoint)
2. Is processing complete? (status should be "completed")
3. Is there an error? (check feedback field)
4. Is session_id correct? (404 error means wrong ID)

**Common Issues:**
- Video upload failed → No processing happens
- Processing crashed → Status stuck at "processing"
- Wrong session_id → 404 error
- Video too large → Processing timeout

---

## Need More Help?

1. Share the session_id
2. Test the API endpoint directly
3. Check Bubble debugger for API response
4. Check browser console for errors
