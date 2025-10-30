# Resume Builder Frontend Integration Guide

## Overview
This guide shows how to integrate the Resume Builder API with your frontend (Bubble.io or custom frontend).

## API Endpoint

```
POST https://interviewbot-rjsi.onrender.com/api/resume-builder/generate
```

## Form Fields Mapping

Based on your UI design, here's how the form fields map to the API:

| UI Field | API Parameter | Type | Required |
|----------|---------------|------|----------|
| "What's your name?" | `name` | string | Yes |
| "What's your course?" | `course` | string | Yes |
| "Education background" | `education_background` | string | Yes |
| "Skills you have" | `skills` | string | Yes |
| "Internship Experience" | `internship_experience` | string | Yes |
| "Anything you want to add?" | `additional_info` | string | No |

## Integration Steps

### For Bubble.io

1. **Create API Connector**
   - Go to Plugins → API Connector
   - Add a new API: "Resume Builder API"
   - Base URL: `https://interviewbot-rjsi.onrender.com`

2. **Add API Call**
   - Name: "Generate Resume"
   - Use as: Action
   - Data type: JSON
   - Method: POST
   - URL: `/api/resume-builder/generate`

3. **Add Parameters**
   ```
   name - text - required
   course - text - required
   education_background - text - required
   skills - text - required
   internship_experience - text - required
   additional_info - text - optional (can be empty)
   ```

4. **Set Body Type**
   - Body type: JSON
   - Body:
   ```json
   {
     "name": "<name>",
     "course": "<course>",
     "education_background": "<education_background>",
     "skills": "<skills>",
     "internship_experience": "<internship_experience>",
     "additional_info": "<additional_info>"
   }
   ```

5. **Initialize the Call**
   - Click "Initialize call"
   - Fill in sample data
   - Save the response structure

6. **Create Workflow**
   - On button "submit" click
   - Action: Plugins → Resume Builder API - Generate Resume
   - Map input fields to parameters:
     - name = Input Name's value
     - course = Input Course's value
     - education_background = Input Education's value
     - skills = Input Skills's value
     - internship_experience = Input Internship's value
     - additional_info = Input Additional's value

7. **Display Results**
   - Show popup or navigate to results page
   - Display: Result of Step 1's resume_text
   - Display suggestions: Result of Step 1's suggestions

### For React/JavaScript Frontend

```javascript
import React, { useState } from 'react';

function ResumeBuilder() {
  const [formData, setFormData] = useState({
    name: '',
    course: '',
    education_background: '',
    skills: '',
    internship_experience: '',
    additional_info: ''
  });
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        'https://interviewbot-rjsi.onrender.com/api/resume-builder/generate',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData)
        }
      );

      if (!response.ok) {
        throw new Error('Failed to generate resume');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="resume-builder">
      <h1>Crafting your resume</h1>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>What's your name?</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Type here..."
            required
          />
        </div>

        <div>
          <label>What's your course?</label>
          <input
            type="text"
            name="course"
            value={formData.course}
            onChange={handleChange}
            placeholder="Type here..."
            required
          />
        </div>

        <div>
          <label>Education background</label>
          <textarea
            name="education_background"
            value={formData.education_background}
            onChange={handleChange}
            placeholder="Type here..."
            required
          />
        </div>

        <div>
          <label>Skills you have</label>
          <textarea
            name="skills"
            value={formData.skills}
            onChange={handleChange}
            placeholder="Type here..."
            required
          />
        </div>

        <div>
          <label>Internship Experience</label>
          <textarea
            name="internship_experience"
            value={formData.internship_experience}
            onChange={handleChange}
            placeholder="Type here..."
            required
          />
        </div>

        <div>
          <label>Anything you want to add?</label>
          <textarea
            name="additional_info"
            value={formData.additional_info}
            onChange={handleChange}
            placeholder="Type here..."
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Submit'}
        </button>
      </form>

      {error && (
        <div className="error">
          Error: {error}
        </div>
      )}

      {result && (
        <div className="result">
          <h2>Your Resume</h2>
          <pre>{result.resume_text}</pre>
          
          <h3>Suggestions for Improvement</h3>
          <ul>
            {result.suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ResumeBuilder;
```

### For HTML/Vanilla JavaScript

```html
<!DOCTYPE html>
<html>
<head>
  <title>Resume Builder</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    .form-group {
      margin-bottom: 20px;
    }
    label {
      display: block;
      margin-bottom: 5px;
      font-weight: bold;
    }
    input, textarea {
      width: 100%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    textarea {
      min-height: 100px;
    }
    button {
      background: #4CAF50;
      color: white;
      padding: 12px 24px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
    }
    button:disabled {
      background: #ccc;
    }
    .result {
      margin-top: 30px;
      padding: 20px;
      background: #f5f5f5;
      border-radius: 4px;
    }
    pre {
      white-space: pre-wrap;
      background: white;
      padding: 15px;
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <h1>Crafting your resume</h1>
  
  <form id="resumeForm">
    <div class="form-group">
      <label>What's your name?</label>
      <input type="text" id="name" required placeholder="Type here...">
    </div>

    <div class="form-group">
      <label>What's your course?</label>
      <input type="text" id="course" required placeholder="Type here...">
    </div>

    <div class="form-group">
      <label>Education background</label>
      <textarea id="education_background" required placeholder="Type here..."></textarea>
    </div>

    <div class="form-group">
      <label>Skills you have</label>
      <textarea id="skills" required placeholder="Type here..."></textarea>
    </div>

    <div class="form-group">
      <label>Internship Experience</label>
      <textarea id="internship_experience" required placeholder="Type here..."></textarea>
    </div>

    <div class="form-group">
      <label>Anything you want to add?</label>
      <textarea id="additional_info" placeholder="Type here..."></textarea>
    </div>

    <button type="submit">Submit</button>
  </form>

  <div id="result" class="result" style="display: none;">
    <h2>Your Resume</h2>
    <pre id="resumeText"></pre>
    
    <h3>Suggestions for Improvement</h3>
    <ul id="suggestions"></ul>
  </div>

  <script>
    document.getElementById('resumeForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const button = e.target.querySelector('button');
      button.disabled = true;
      button.textContent = 'Generating...';

      const formData = {
        name: document.getElementById('name').value,
        course: document.getElementById('course').value,
        education_background: document.getElementById('education_background').value,
        skills: document.getElementById('skills').value,
        internship_experience: document.getElementById('internship_experience').value,
        additional_info: document.getElementById('additional_info').value
      };

      try {
        const response = await fetch(
          'https://interviewbot-rjsi.onrender.com/api/resume-builder/generate',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
          }
        );

        if (!response.ok) {
          throw new Error('Failed to generate resume');
        }

        const data = await response.json();
        
        // Display results
        document.getElementById('resumeText').textContent = data.resume_text;
        
        const suggestionsList = document.getElementById('suggestions');
        suggestionsList.innerHTML = '';
        data.suggestions.forEach(suggestion => {
          const li = document.createElement('li');
          li.textContent = suggestion;
          suggestionsList.appendChild(li);
        });
        
        document.getElementById('result').style.display = 'block';
        
      } catch (error) {
        alert('Error: ' + error.message);
      } finally {
        button.disabled = false;
        button.textContent = 'Submit';
      }
    });
  </script>
</body>
</html>
```

## Response Format

The API returns:

```json
{
  "success": true,
  "resume_text": "JOHN DOE\n========\n\nPROFESSIONAL SUMMARY\n...",
  "resume_html": null,
  "suggestions": [
    "Add specific GPA or academic achievements",
    "Quantify your achievements with metrics",
    "Include relevant coursework or projects"
  ]
}
```

## Error Handling

Handle these potential errors:

```javascript
try {
  const response = await fetch(API_URL, options);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate resume');
  }
  
  const data = await response.json();
  // Handle success
  
} catch (error) {
  // Display error to user
  console.error('Resume generation failed:', error);
}
```

## Tips for Best Results

1. **Provide detailed information**: The more specific the input, the better the resume
2. **Use proper formatting**: Separate items with line breaks
3. **Be specific**: Include actual technologies, companies, dates
4. **Quantify achievements**: Include numbers and metrics
5. **Review suggestions**: Apply relevant AI suggestions

## Testing

Test the API with this sample data:

```json
{
  "name": "Jane Smith",
  "course": "Computer Science",
  "education_background": "National University of Singapore\nBachelor of Computing in Computer Science\n2020 - 2024\nGPA: 4.5/5.0",
  "skills": "Python, JavaScript, React, Node.js, SQL, Git, AWS, Docker, Machine Learning",
  "internship_experience": "Software Engineering Intern at Tech Startup\nJune 2023 - August 2023\n- Developed RESTful APIs using Node.js and Express\n- Implemented frontend features with React and TypeScript\n- Improved application performance by 30%\n- Collaborated with team of 5 developers using Agile methodology",
  "additional_info": "President of Computer Science Club\nHackathon Winner - NUS Hack&Roll 2023\nVolunteer tutor for underprivileged students\nPublished research paper on ML applications"
}
```

## Support

For issues or questions:
- Check the full API documentation: `RESUME_BUILDER_API.md`
- GitHub: https://github.com/jialekhooo/interviewbot
