# Bubble.io Video Interview Workflow - Complete Guide

## Overview

Your backend supports **5 video interview questions**. Each question creates a separate session, so you need to:
1. Loop through questions 1-5
2. Create a session for each question
3. Upload video for each session
4. Track all 5 session IDs
5. Fetch all results together using the batch endpoint

---

## Step 1: API Connector Setup

### **API Call 1: Start Video Interview**

**Name:** Start Video Interview  
**Use as:** Action  
**Data type:** JSON

**Configuration:**
- **Method:** POST
- **URL:** `https://interviewbot-rjsi.onrender.com/api/video-interview/start`
- **Body type:** Form-data

**Parameters:**
| Key | Type | Private | Test Value |
|-----|------|---------|------------|
| `user_id` | text | ☐ | test123 |
| `position` | text | ☐ | Software Engineer |
| `question_number` | number | ☐ | 1 |

**Response:**
```json
{
  "session_id": "uuid",
  "question": "Tell me about yourself...",
  "question_number": 1,
  "position": "Software Engineer",
  "tips": [...],
  "max_questions": 5,
  "status": "pending"
}
```

---

### **API Call 2: Upload Video**

**Name:** Upload Video Interview  
**Use as:** Action  
**Data type:** JSON

**Configuration:**
- **Method:** POST
- **URL:** `https://interviewbot-rjsi.onrender.com/api/video-interview/upload/<session_id>`
- **Body type:** Form-data

**Parameters:**
| Key | Type | Private | Test Value |
|-----|------|---------|------------|
| `session_id` | text | ☐ | test-uuid |
| `video` | file | ☐ | (upload test video) |

---

### **API Call 3: Get Batch Results** ⭐ (NEW)

**Name:** Get Batch Video Interview Results  
**Use as:** Data  
**Data type:** JSON

**Configuration:**
- **Method:** POST
- **URL:** `https://interviewbot-rjsi.onrender.com/api/video-interview/results/batch`
- **Body type:** JSON

**Body:**
```json
{
  "session_ids": ["id1", "id2", "id3", "id4", "id5"]
}
```

**Response:**
```json
{
  "total": 5,
  "completed": 5,
  "processing": 0,
  "failed": 0,
  "all_completed": true,
  "results": [
    {
      "session_id": "...",
      "question": "Tell me about yourself...",
      "status": "completed",
      "transcript": "I am a software engineer...",
      "feedback": "Great answer!...",
      "scores": {
        "overall_score": 85,
        "communication": 90,
        "content": 80
      }
    },
    ... (4 more results)
  ]
}
```

---

## Step 2: Page Custom States

On your **Video Interview page**, add these custom states:

| State Name | Type | Default Value | Description |
|------------|------|---------------|-------------|
| `session_ids` | text (list) | empty list | Stores all 5 session IDs |
| `current_question` | number | 1 | Current question number (1-5) |
| `current_session_id` | text | empty | Current session ID |
| `current_question_text` | text | empty | Current question text |
| `videos_uploaded` | number | 0 | Count of uploaded videos |
| `all_uploaded` | yes/no | no | All 5 videos uploaded? |

---

## Step 3: Workflows

### **Workflow 1: Start First Question**

**Event:** When Button "Start Interview" is clicked

**Actions:**
```
Step 1: Start Video Interview (API)
  → user_id = Current User's unique id
  → position = Input Position's value
  → question_number = 1

Step 2: Set State - current_session_id
  → Element: This page
  → Value: Result of Step 1's session_id

Step 3: Set State - current_question_text
  → Element: This page
  → Value: Result of Step 1's question

Step 4: Set State - current_question
  → Element: This page
  → Value: 1

Step 5: Add to list - session_ids
  → Element: This page
  → Custom state: session_ids
  → Value: Result of Step 1's session_id
```

---

### **Workflow 2: Submit Video and Move to Next Question**

**Event:** When Button "Submit Video" is clicked

**Actions:**
```
Step 1: Upload Video Interview (API)
  → session_id = This page's current_session_id
  → video = VideoRecorder's value

Step 2: Set State - videos_uploaded
  → Element: This page
  → Value: This page's videos_uploaded + 1

Step 3: Only when This page's videos_uploaded < 5
  → Start Video Interview (API)
    → user_id = Current User's unique id
    → position = Input Position's value
    → question_number = This page's current_question + 1
  
  → Set State - current_session_id
    → Value: Result's session_id
  
  → Set State - current_question_text
    → Value: Result's question
  
  → Set State - current_question
    → Value: Result's question_number
  
  → Add to list - session_ids
    → Value: Result's session_id

Step 4: Only when This page's videos_uploaded = 5
  → Set State - all_uploaded = yes
  → Show Popup Video Interview Results
```

---

### **Workflow 3: Fetch All Results When Popup Opens**

**Event:** When Popup Video Interview Results is displayed

**Actions:**
```
Step 1: Get Batch Video Interview Results (API)
  → session_ids = This page's session_ids
```

---

### **Workflow 4: Poll for Processing**

**Event:** Do every 5 seconds

**Condition - Only when:**
- `Popup Video Interview Results is visible` **is** `yes`
- **AND** `Get Batch Video Interview Results's all_completed` **is** `no`

**Actions:**
```
Step 1: Get Batch Video Interview Results (API)
  → session_ids = This page's session_ids

Step 2: Only when Get Batch Video Interview Results's all_completed is yes
  → Stop this workflow (optional - will stop automatically)
```

---

## Step 4: Popup Design

### **Popup: Video Interview Results**

**Elements:**

#### **Group: Loading** (Visible when all_completed = no)
```
Icon: Loading spinner
Text: "Processing your interviews... Please wait."
Text: "Completed: [Get Batch Video Interview Results's completed] / 5"
```

#### **Group: Results** (Visible when all_completed = yes)
```
Repeating Group: All Results
  → Data source: Get Batch Video Interview Results's results
  → Type: (auto-detected from API)
  
  Inside each cell:
    Text: "Question [Current cell's index]"
    Text: Current cell's question
    Text: "Your Answer:"
    Text: Current cell's transcript
    Text: "Feedback:"
    Text: Current cell's feedback
    Text: "Score: [Current cell's scores's overall_score]/100"
```

#### **Group: Error** (Visible when failed > 0)
```
Text: "Some videos failed to process. Please try again."
```

---

## Step 5: Display Elements

### **Question Display (During Interview)**
```
Text: Question [This page's current_question] of 5
Text: This page's current_question_text
```

### **Progress Indicator**
```
Text: "Videos uploaded: [This page's videos_uploaded] / 5"
Progress Bar: This page's videos_uploaded / 5 * 100%
```

---

## Complete Flow Diagram

```
User clicks "Start Interview"
  ↓
Question 1:
  - Start Video Interview (API) → Get question 1
  - Save session_id to list
  - Display question
  - User records video
  - User clicks "Submit Video"
  - Upload Video (API)
  - videos_uploaded = 1
  ↓
Question 2:
  - Start Video Interview (API) → Get question 2
  - Save session_id to list
  - Display question
  - User records video
  - User clicks "Submit Video"
  - Upload Video (API)
  - videos_uploaded = 2
  ↓
Question 3, 4, 5... (same pattern)
  ↓
After Question 5:
  - videos_uploaded = 5
  - all_uploaded = yes
  - Show Popup
  ↓
Popup opens:
  - Get Batch Video Interview Results (API)
  - Pass all 5 session_ids
  ↓
Poll every 5 seconds:
  - Get Batch Video Interview Results (API)
  - Check all_completed
  ↓
When all_completed = true:
  - Display all 5 results in repeating group
  - Stop polling
```

---

## Example Workflow Summary

### **Your Current Workflow (Wrong):**
```
Do every time:
  Only when: User Interview Sessions Vids:last item's Answers:count > 4
  → This checks TEXT interview data ❌
```

### **Correct Workflow (New):**
```
Do every 5 seconds:
  Only when:
    - Popup is visible
    - Get Batch Video Interview Results's all_completed is no
  
  Step 1: Get Batch Video Interview Results
    → session_ids = This page's session_ids
```

---

## Key Differences

| Old (Text Interview) | New (Video Interview) |
|---------------------|----------------------|
| User Interview Sessions | Get Batch Video Interview Results |
| Answers:count > 4 | all_completed is yes |
| Progress is not End | all_completed is no |
| Single session | 5 separate sessions |
| Database data | API data |

---

## Testing Checklist

- [ ] Start interview → Question 1 appears
- [ ] Submit video 1 → Question 2 appears
- [ ] Submit video 2 → Question 3 appears
- [ ] Submit video 3 → Question 4 appears
- [ ] Submit video 4 → Question 5 appears
- [ ] Submit video 5 → Popup appears
- [ ] Popup shows "Processing..." initially
- [ ] After 10-30 seconds, all 5 results appear
- [ ] Each result shows: question, transcript, feedback, score
- [ ] All 5 session IDs are in the list

---

## Debugging

### **If questions don't advance:**
- Check: Is current_question being incremented?
- Check: Is Start Video Interview being called after each upload?

### **If popup doesn't show:**
- Check: Is all_uploaded being set to yes after 5th upload?
- Check: Is videos_uploaded = 5?

### **If results don't appear:**
- Check: Are all 5 session_ids in the list?
- Check: Is Get Batch Video Interview Results being called?
- Check: Open debugger, see API response

### **If stuck at "Processing...":**
- Check: Is polling workflow running?
- Check: What is all_completed value?
- Check: Individual video statuses in API response

---

## Summary

✅ **Use the new batch endpoint** - Fetches all 5 results at once  
✅ **Track session_ids in a list** - Save each session ID  
✅ **Poll for all_completed** - Check when all are done  
✅ **Display in repeating group** - Show all 5 results together  

**This is much simpler than your current workflow and designed specifically for video interviews!**
