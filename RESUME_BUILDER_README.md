# Resume Builder Feature Documentation

## Overview
The Resume Builder feature allows users to create professional resumes by filling out a simple form. The system uses OpenAI to generate well-structured, ATS-friendly resumes with personalized suggestions for improvement.

## Features Implemented

### Backend Components

#### 1. Schemas (`app/schemas/resume_builder.py`)
- **ResumeBuilderRequest**: Input schema for resume generation
  - name, major, education_background
  - skills, internship_experience
  - additional_info (optional)
  
- **ResumeBuilderResponse**: Output schema
  - success status
  - resume_text (generated resume)
  - suggestions (improvement tips)

#### 2. Service (`app/services/resume_builder_service.py`)

**ResumeBuilderService** (Real AI Service):
- Uses OpenAI GPT-4o-mini for resume generation
- Creates professional, ATS-friendly resumes
- Generates personalized improvement suggestions
- Structured output with clear sections

**FakeResumeBuilderService** (Testing Service):
- Mock service for development without API key
- Returns realistic sample resumes
- Provides generic improvement suggestions
- Currently active by default

#### 3. API Router (`app/routers/resume_builder.py`)

**Endpoints:**

**POST `/api/resume-builder/generate`**
- Generates complete professional resume
- Returns formatted resume text and suggestions
- Requires: name, major, education, skills, experience

**POST `/api/resume-builder/preview`**
- Quick preview without saving
- Same output as generate endpoint

**POST `/api/resume-builder/improve`**
- Get suggestions for specific resume section
- Future enhancement endpoint

### Frontend Component

#### Resume Builder Page (`frontend/src/pages/ResumeBuilder.jsx`)

**Form Fields:**
1. **Name** - User's full name
2. **Major** - Field of study/specialization
3. **Education Background** - Degree, university, dates
4. **Skills** - Technical and soft skills
5. **Internship Experience** - Work experience details
6. **Additional Info** - Awards, certifications, projects (optional)

**Features:**
- ✅ Clean, intuitive form interface
- ✅ Real-time validation
- ✅ Loading states with animations
- ✅ Generated resume display
- ✅ AI-powered improvement suggestions
- ✅ Download resume as text file
- ✅ Start over functionality
- ✅ Responsive design
- ✅ Error handling

**UI Elements:**
- Pencil icon header
- Two-column layout (form + results)
- Professional styling matching screenshot
- Download button for generated resume
- Numbered suggestion list
- Scrollable resume preview

## How It Works

### User Flow
1. User fills out the resume builder form
2. Clicks "Submit" button
3. System sends data to backend API
4. OpenAI generates professional resume
5. Resume displayed with improvement suggestions
6. User can download or start over

### Technical Flow
1. Frontend validates form data
2. POST request to `/api/resume-builder/generate`
3. Backend calls OpenAI with structured prompt
4. AI generates resume with proper formatting
5. AI generates improvement suggestions
6. Response sent back to frontend
7. Resume displayed in formatted view

## API Usage

### Generate Resume

**Request:**
```javascript
POST /api/resume-builder/generate

{
  "name": "Jia Le",
  "major": "Electrical Engineering",
  "education_background": "Bachelor of Science in EEE, XYZ University, 2020-2024",
  "skills": "Python, Java, Circuit Design, MATLAB",
  "internship_experience": "Software Engineering Intern at ABC Company...",
  "additional_info": "Dean's List, IEEE Member"
}
```

**Response:**
```javascript
{
  "success": true,
  "resume_text": "JIA LE\n======\n\nPROFESSIONAL SUMMARY\n...",
  "suggestions": [
    "Add specific GPA or academic achievements",
    "Quantify internship achievements with metrics",
    ...
  ]
}
```

## Resume Structure

The AI generates resumes with these sections:

1. **Header** - Name and contact info
2. **Professional Summary** - Brief overview
3. **Education** - Degree, institution, dates
4. **Technical Skills** - Listed skills
5. **Professional Experience** - Internships/work
6. **Additional Information** - Awards, certifications
7. **Achievements & Interests** - Optional extras

## AI Prompts

### Resume Generation Prompt
- Creates professional, ATS-friendly format
- Uses action verbs and strong language
- Structures information clearly
- Tailors to candidate's strengths
- Ensures grammatical correctness

### Suggestions Prompt
- Identifies missing information
- Recommends quantifiable achievements
- Suggests formatting improvements
- Provides actionable feedback

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_api_key_here  # Required for real AI service
```

### Enable Real AI Service
In `app/services/resume_builder_service.py`:
```python
# Uncomment this line:
resume_builder_service = ResumeBuilderService() if os.getenv("OPENAI_API_KEY") else FakeResumeBuilderService()
```

## Testing

### With Fake Service (Default)
- No API key required
- Returns mock resume immediately
- Good for UI/UX testing
- Generic but realistic output

### With Real Service
- Requires OpenAI API key
- Generates personalized resumes
- Tailored suggestions
- Higher quality output

## Features

### Current Features
✅ Form-based resume input
✅ AI-powered resume generation
✅ Improvement suggestions
✅ Download as text file
✅ Responsive design
✅ Error handling
✅ Loading states

### Future Enhancements
- 📄 PDF export
- 🎨 Multiple resume templates
- 💾 Save resume to database
- 📧 Email resume
- 🔄 Edit and regenerate
- 📊 Resume scoring
- 🎯 Job-specific tailoring
- 📝 Cover letter generation

## Integration

### Main Application
The resume builder is integrated in `app/main.py`:
```python
from app.routers import resume_builder
app.include_router(resume_builder.router, prefix="/api/resume-builder", tags=["resume_builder"])
```

### Frontend Routing
Added to `frontend/src/App.jsx`:
```javascript
<Route path="/resume-builder" element={<ResumeBuilder />} />
```

### Navigation
Link added to main navigation bar

## File Structure

```
Backend:
├── app/
│   ├── routers/
│   │   └── resume_builder.py          # API endpoints
│   ├── schemas/
│   │   └── resume_builder.py          # Request/response models
│   └── services/
│       └── resume_builder_service.py  # AI service logic

Frontend:
└── frontend/src/pages/
    └── ResumeBuilder.jsx              # UI component
```

## Dependencies

### Backend
- OpenAI SDK (already in requirements.txt)
- FastAPI (already installed)
- Pydantic (already installed)

### Frontend
- React (already installed)
- Heroicons (already installed)
- Axios (already installed)

## Example Output

```
JIA LE
======

PROFESSIONAL SUMMARY
-------------------
Motivated Electrical Engineering student with strong foundation in 
circuit design and programming. Proven ability to apply theoretical 
knowledge in practical settings through internship experience.

EDUCATION
---------
Bachelor of Science in Electrical Engineering
XYZ University, 2020-2024

TECHNICAL SKILLS
---------------
- Programming: Python, Java, MATLAB
- Engineering: Circuit Design, Signal Processing
- Tools: AutoCAD, Simulink

PROFESSIONAL EXPERIENCE
----------------------
Software Engineering Intern | ABC Company | Summer 2023
- Developed web applications using React and Python
- Collaborated with team of 5 engineers on product features
- Improved code efficiency by 25% through optimization

ADDITIONAL INFORMATION
-------------------
- Dean's List (2021-2023)
- IEEE Student Member
- Fluent in English and Mandarin
```

## Troubleshooting

### Resume Not Generating
- Check if form fields are filled
- Verify backend is running
- Check browser console for errors

### API Errors
- Ensure OpenAI API key is set (for real service)
- Check API rate limits
- Verify network connection

### Download Not Working
- Check browser download permissions
- Ensure resume was generated successfully

## Summary

The Resume Builder feature is **fully implemented and functional**:
- ✅ Complete backend API with AI integration
- ✅ Professional frontend interface
- ✅ Form validation and error handling
- ✅ Download functionality
- ✅ Improvement suggestions
- ✅ Works with fake service (no API key needed)
- ✅ Can be upgraded to real AI service easily

Navigate to `/resume-builder` to start creating professional resumes!
