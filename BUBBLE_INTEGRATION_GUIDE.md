# 🔗 Bubble.io Integration Guide

## 📋 Overview
This guide will help you connect your Interview Chatbot backend to Bubble.io frontend.

## 🚀 Backend Endpoints for Bubble.io

### Base URL
```
https://interviewbot-rjsi.onrender.com
```

### 🎯 Bubble-Optimized Endpoints

#### 1. Start Interview
```
POST /api/bubble/interview/start
Content-Type: application/json

Body:
{
  "position": "Software Engineer",
  "difficulty": "medium",
  "question_types": ["behavioral", "technical"],
  "duration": 30
}

Response:
{
  "success": true,
  "message": "Interview started successfully",
  "data": {
    "session_id": "uuid-here",
    "question": "Tell me about yourself...",
    "status": "active",
    "position": "Software Engineer",
    "difficulty": "medium"
  }
}
```

#### 2. Submit Answer
```
POST /api/bubble/interview/answer
Content-Type: application/json

Body:
{
  "session_id": "uuid-from-start",
  "response": "I am a software engineer with 3 years experience...",
  "time_taken": 120
}

Response:
{
  "success": true,
  "message": "Answer processed successfully", 
  "data": {
    "feedback": "Great answer! You clearly explained...",
    "score": 8,
    "next_question": "What's your biggest strength?",
    "session_id": "uuid-here"
  }
}
```

#### 3. Analyze Resume
```
POST /api/bubble/resume/analyze
Content-Type: application/json

Body:
{
  "resume_text": "John Doe\nSoftware Engineer\n...",
  "target_role": "Senior Developer"
}

Response:
{
  "success": true,
  "message": "Resume analyzed successfully",
  "data": {
    "analysis": "Your resume shows strong technical skills...",
    "score": 7.5,
    "target_role": "Senior Developer"
  }
}
```

#### 4. Get Answer Guidance
```
POST /api/bubble/guidance/improve
Content-Type: application/json

Body:
{
  "question": "Tell me about a challenging project",
  "user_answer": "I worked on a web app...",
  "context": "Technical interview"
}

Response:
{
  "success": true,
  "message": "Guidance generated successfully",
  "data": {
    "guidance": "Good start! To improve, add specific metrics...",
    "question": "Tell me about a challenging project",
    "improved_answer": "See guidance for specific improvements"
  }
}
```

## 🛠️ Bubble.io Setup Instructions

### Step 1: Install API Connector Plugin
1. Go to your Bubble.io app
2. Click **Plugins** → **Add plugins**
3. Search for **"API Connector"**
4. Install and add to your app

### Step 2: Configure API Calls

#### API Call 1: Start Interview
```
Name: Start Interview
Use as: Action
Method: POST
URL: https://interviewbot-rjsi.onrender.com/api/bubble/interview/start
Headers:
  Content-Type: application/json
Body type: JSON
Body:
{
  "position": "<position>",
  "difficulty": "<difficulty>", 
  "question_types": ["<question_type>"],
  "duration": <duration>
}
```

#### API Call 2: Submit Answer
```
Name: Submit Answer
Use as: Action
Method: POST
URL: https://interviewbot-rjsi.onrender.com/api/bubble/interview/answer
Headers:
  Content-Type: application/json
Body type: JSON
Body:
{
  "session_id": "<session_id>",
  "response": "<user_answer>",
  "time_taken": <time_taken>
}
```

#### API Call 3: Analyze Resume
```
Name: Analyze Resume
Use as: Action
Method: POST
URL: https://interviewbot-rjsi.onrender.com/api/bubble/resume/analyze
Headers:
  Content-Type: application/json
Body type: JSON
Body:
{
  "resume_text": "<resume_text>",
  "target_role": "<target_role>"
}
```

### Step 3: Create Data Types

#### Interview Session
- session_id (text)
- current_question (text)
- status (text)
- position (text)
- difficulty (text)

#### Interview Response
- feedback (text)
- score (number)
- next_question (text)

### Step 4: Build UI Elements

#### Interview Page Elements:
1. **Input: Position** (dropdown: Software Engineer, Data Scientist, etc.)
2. **Input: Difficulty** (dropdown: easy, medium, hard)
3. **Button: Start Interview**
4. **Text: Current Question** (dynamic)
5. **Input: User Answer** (multiline)
6. **Button: Submit Answer**
7. **Text: Feedback** (dynamic)
8. **Text: Score** (dynamic)

#### Resume Analysis Page Elements:
1. **Input: Resume Text** (multiline)
2. **Input: Target Role** (text)
3. **Button: Analyze Resume**
4. **Text: Analysis Result** (dynamic)
5. **Text: Score** (dynamic)

### Step 5: Create Workflows

#### Workflow 1: Start Interview
**Trigger:** Button "Start Interview" is clicked
**Actions:**
1. **API Call: Start Interview**
   - position = Input Position's value
   - difficulty = Input Difficulty's value
   - question_types = ["behavioral"]
   - duration = 30

2. **Set state: session_id** = Result of step 1's data session_id
3. **Set state: current_question** = Result of step 1's data question
4. **Show/Hide elements** (hide start form, show interview form)

#### Workflow 2: Submit Answer
**Trigger:** Button "Submit Answer" is clicked
**Actions:**
1. **API Call: Submit Answer**
   - session_id = session_id state
   - response = Input User Answer's value
   - time_taken = 60

2. **Set state: feedback** = Result of step 1's data feedback
3. **Set state: score** = Result of step 1's data score
4. **Set state: current_question** = Result of step 1's data next_question
5. **Reset Input User Answer**

#### Workflow 3: Analyze Resume
**Trigger:** Button "Analyze Resume" is clicked
**Actions:**
1. **API Call: Analyze Resume**
   - resume_text = Input Resume Text's value
   - target_role = Input Target Role's value

2. **Set state: analysis** = Result of step 1's data analysis
3. **Set state: resume_score** = Result of step 1's data score

### Step 6: Error Handling

Add conditions to each workflow:
```
Only when Result of step 1's success is "yes"
```

For error cases, add actions:
```
Display message: Result of step 1's message
```

## 🎨 UI Design Tips

### Colors:
- Primary: #3B82F6 (blue)
- Success: #10B981 (green)
- Warning: #F59E0B (yellow)
- Error: #EF4444 (red)

### Layout:
- Use **Groups** for sections
- Set **responsive** behavior
- Add **loading states** during API calls
- Use **conditional formatting** for scores

## 🧪 Testing

### Test Endpoints:
1. **Health Check:** GET https://interviewbot-rjsi.onrender.com/api/bubble/health
2. **Start Interview:** Use Bubble.io API connector test
3. **Submit Answer:** Test with sample data
4. **Resume Analysis:** Test with sample resume text

## 🚀 Go Live Checklist

- [ ] All API calls configured
- [ ] Data types created
- [ ] Workflows tested
- [ ] Error handling added
- [ ] UI responsive on mobile
- [ ] Loading states implemented
- [ ] Backend deployed and healthy

## 📞 Support

If you need help:
1. Check backend health: `/api/bubble/health`
2. Test individual endpoints with Postman
3. Check Bubble.io debugger for API errors
4. Verify CORS settings (already configured)

Your backend is ready for Bubble.io integration! 🎉
