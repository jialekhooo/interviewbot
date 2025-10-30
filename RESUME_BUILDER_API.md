# Resume Builder API Documentation

## Overview
The Resume Builder API allows users to generate professional resumes using AI based on their personal information, education, skills, and experience.

## Base URL
```
Production: https://interviewbot-rjsi.onrender.com/api/resume-builder
Development: http://localhost:8000/api/resume-builder
```

## Endpoints

### 1. Generate Resume

**POST** `/generate`

Generate a complete professional resume with AI-powered suggestions.

#### Request Body

```json
{
  "name": "John Doe",
  "course": "Computer Science",
  "education_background": "National University of Singapore\nBachelor of Computing in Computer Science\n2020 - 2024\nGPA: 4.5/5.0",
  "skills": "Python, JavaScript, React, Node.js, SQL, Git, AWS, Docker",
  "internship_experience": "Software Engineering Intern at Tech Company\nJune 2023 - August 2023\n- Developed RESTful APIs using Node.js and Express\n- Implemented frontend features with React and TypeScript\n- Collaborated with team of 5 developers using Agile methodology",
  "additional_info": "President of Computer Science Club\nHackathon Winner - NUS Hack&Roll 2023\nVolunteer tutor for underprivileged students",
  "user_id": "optional_user_id"
}
```

#### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Full name of the candidate |
| `course` | string | Yes | Course/field of study |
| `education_background` | string | Yes | Educational background details |
| `skills` | string | Yes | Technical and soft skills |
| `internship_experience` | string | Yes | Work experience and internships |
| `additional_info` | string | No | Additional achievements, activities, etc. |
| `user_id` | string | No | Optional user identifier |

#### Response

```json
{
  "success": true,
  "resume_text": "JOHN DOE\n========\n\nPROFESSIONAL SUMMARY\n-------------------\nMotivated Computer Science student with a strong foundation in technical and analytical skills...\n\nEDUCATION\n---------\nNational University of Singapore\nBachelor of Computing in Computer Science\n2020 - 2024\nGPA: 4.5/5.0\n\nTECHNICAL SKILLS\n---------------\nPython, JavaScript, React, Node.js, SQL, Git, AWS, Docker\n\n...",
  "resume_html": null,
  "suggestions": [
    "Add specific GPA or academic achievements to strengthen your education section",
    "Quantify your internship achievements with metrics (e.g., 'Improved efficiency by 20%')",
    "Include relevant coursework or projects that demonstrate your skills",
    "Add certifications or online courses relevant to your field",
    "Consider adding a LinkedIn profile or portfolio link to your contact information"
  ]
}
```

#### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the resume generation was successful |
| `resume_text` | string | The generated resume in plain text format |
| `resume_html` | string \| null | HTML version of the resume (currently null) |
| `suggestions` | array | List of improvement suggestions |

#### Status Codes

- `200 OK` - Resume generated successfully
- `422 Unprocessable Entity` - Invalid request body
- `500 Internal Server Error` - Resume generation failed

---

### 2. Preview Resume

**POST** `/preview`

Generate a quick preview of the resume without authentication or saving.

#### Request Body

Same as `/generate` endpoint (excluding `user_id`).

#### Response

```json
{
  "preview": "JOHN DOE\n========\n\nPROFESSIONAL SUMMARY\n...",
  "suggestions": [
    "Add specific GPA or academic achievements",
    "Quantify your achievements with metrics",
    "Include relevant coursework or projects"
  ]
}
```

#### Status Codes

- `200 OK` - Preview generated successfully
- `422 Unprocessable Entity` - Invalid request body
- `500 Internal Server Error` - Preview generation failed

---

### 3. Improve Resume Section

**POST** `/improve`

Get AI-powered suggestions to improve a specific section of the resume.

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `section` | string | Yes | Section name (e.g., "experience", "skills") |
| `content` | string | Yes | Current content of the section |

#### Response

```json
{
  "section": "experience",
  "original": "Worked as intern at company",
  "suggestions": [
    "Use more action verbs to start bullet points",
    "Add quantifiable metrics and achievements",
    "Be more specific about your contributions"
  ]
}
```

#### Status Codes

- `200 OK` - Suggestions generated successfully
- `500 Internal Server Error` - Failed to generate suggestions

---

## Example Usage

### cURL

```bash
# Generate Resume
curl -X POST "https://interviewbot-rjsi.onrender.com/api/resume-builder/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "course": "Computer Science",
    "education_background": "NUS\nBachelor of Computing\n2020-2024",
    "skills": "Python, JavaScript, React",
    "internship_experience": "Software Intern at Tech Co\nJune 2023 - Aug 2023",
    "additional_info": "Hackathon Winner"
  }'
```

### JavaScript (Fetch)

```javascript
const response = await fetch('https://interviewbot-rjsi.onrender.com/api/resume-builder/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'John Doe',
    course: 'Computer Science',
    education_background: 'NUS\nBachelor of Computing\n2020-2024',
    skills: 'Python, JavaScript, React',
    internship_experience: 'Software Intern at Tech Co\nJune 2023 - Aug 2023',
    additional_info: 'Hackathon Winner'
  })
});

const data = await response.json();
console.log(data.resume_text);
console.log(data.suggestions);
```

### Python (Requests)

```python
import requests

url = "https://interviewbot-rjsi.onrender.com/api/resume-builder/generate"
payload = {
    "name": "John Doe",
    "course": "Computer Science",
    "education_background": "NUS\nBachelor of Computing\n2020-2024",
    "skills": "Python, JavaScript, React",
    "internship_experience": "Software Intern at Tech Co\nJune 2023 - Aug 2023",
    "additional_info": "Hackathon Winner"
}

response = requests.post(url, json=payload)
data = response.json()

print(data["resume_text"])
print(data["suggestions"])
```

## AI Service

The API uses OpenAI's GPT-4o-mini model to generate professional resumes. The service:

- Creates well-structured, ATS-friendly resumes
- Uses action-oriented language with strong verbs
- Provides personalized suggestions for improvement
- Formats content professionally with clear sections

### Fallback Mode

If OpenAI API is unavailable, the service falls back to a template-based generator that still provides:
- Structured resume format
- Professional layout
- Generic improvement suggestions

## Rate Limiting

Currently, there are no rate limits on the API. However, please use responsibly to avoid overloading the service.

## Authentication

Authentication is optional for resume generation. If you want to associate resumes with specific users:

1. Include authentication token in headers (if using auth system)
2. Or provide `user_id` in the request body

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common errors:
- Missing required fields → 422 Unprocessable Entity
- Invalid data format → 422 Unprocessable Entity
- AI service failure → 500 Internal Server Error

## Best Practices

1. **Provide detailed information**: The more specific and detailed your input, the better the generated resume
2. **Use proper formatting**: Use line breaks (`\n`) to separate different items in education and experience
3. **Be specific with skills**: List actual technologies, tools, and frameworks rather than generic terms
4. **Quantify achievements**: Include numbers, percentages, and metrics in your experience
5. **Review suggestions**: Always review the AI-generated suggestions and apply relevant ones

## Support

For issues or questions:
- GitHub: https://github.com/jialekhooo/interviewbot
- Email: support@example.com (update with actual email)

## Changelog

### Version 1.0.0 (Current)
- Initial release
- Generate resume endpoint
- Preview endpoint
- Improve section endpoint
- AI-powered suggestions
- Fallback template mode
