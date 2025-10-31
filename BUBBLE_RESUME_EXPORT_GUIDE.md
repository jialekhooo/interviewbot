# Resume Export API Guide for Bubble.io

This guide explains how to integrate the PDF and DOCX resume export endpoints with your Bubble.io frontend.

## New Endpoints

### 1. Generate PDF Resume
**Endpoint:** `POST /api/resume-builder/generate-pdf`

**Request Body:**
```json
{
  "name": "John Doe",
  "course": "Computer Science",
  "education_background": "Bachelor of Science in Computer Science, XYZ University, 2020-2024",
  "skills": "Python, JavaScript, React, FastAPI",
  "internship_experience": "Software Engineering Intern at ABC Company (Summer 2023)",
  "additional_info": "Dean's List, Hackathon Winner",
  "user_id": "optional_user_id"
}
```

**Response:**
- Content-Type: `application/pdf`
- Returns a downloadable PDF file
- Filename: `{Name}_Resume.pdf`

---

### 2. Generate DOCX Resume
**Endpoint:** `POST /api/resume-builder/generate-docx`

**Request Body:** (Same as PDF endpoint)
```json
{
  "name": "John Doe",
  "course": "Computer Science",
  "education_background": "Bachelor of Science in Computer Science, XYZ University, 2020-2024",
  "skills": "Python, JavaScript, React, FastAPI",
  "internship_experience": "Software Engineering Intern at ABC Company (Summer 2023)",
  "additional_info": "Dean's List, Hackathon Winner",
  "user_id": "optional_user_id"
}
```

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Returns a downloadable DOCX file
- Filename: `{Name}_Resume.docx`

---

## Setting Up in Bubble.io

### Step 1: Add API Connector Plugin
1. Go to **Plugins** tab in Bubble
2. Add the **API Connector** plugin if not already installed

### Step 2: Configure API Calls

#### For PDF Export:
1. In API Connector, click **Add another API**
2. Name it: `Resume Builder API`
3. Add a new call: `Generate PDF Resume`
4. Settings:
   - **Use as:** Action
   - **Data type:** File
   - **Method:** POST
   - **URL:** `https://your-backend-url.com/api/resume-builder/generate-pdf`
   - **Body type:** JSON
   - **Body:**
     ```json
     {
       "name": "<name>",
       "course": "<course>",
       "education_background": "<education_background>",
       "skills": "<skills>",
       "internship_experience": "<internship_experience>",
       "additional_info": "<additional_info>",
       "user_id": "<user_id>"
     }
     ```
   - **Headers:**
     - `Content-Type: application/json`

#### For DOCX Export:
1. Add another call: `Generate DOCX Resume`
2. Same settings as PDF, but change URL to:
   - **URL:** `https://your-backend-url.com/api/resume-builder/generate-docx`

### Step 3: Create Buttons in Bubble

#### PDF Download Button:
1. Add a button: "Download as PDF"
2. Add workflow: **When Button is clicked**
3. Action: **Plugins > Resume Builder API - Generate PDF Resume**
4. Set parameters from input fields:
   - name = `Input Name's value`
   - course = `Input Course's value`
   - education_background = `Input Education's value`
   - skills = `Input Skills's value`
   - internship_experience = `Input Experience's value`
   - additional_info = `Input Additional's value`
5. Add action: **Download file**
   - File to download: `Result of step 1`

#### DOCX Download Button:
1. Add a button: "Download as Word"
2. Same workflow as PDF, but use **Generate DOCX Resume** action

---

## Example Workflow in Bubble

```
User fills form → Clicks "Download PDF" → 
API call to /generate-pdf → 
Receives PDF file → 
Browser downloads file automatically
```

---

## Testing the Endpoints

### Using cURL (for testing):

**Test PDF Generation:**
```bash
curl -X POST "http://localhost:8000/api/resume-builder/generate-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "course": "Computer Science",
    "education_background": "BS Computer Science, Test University",
    "skills": "Python, JavaScript",
    "internship_experience": "Software Intern at Test Company",
    "additional_info": "Dean List"
  }' \
  --output test_resume.pdf
```

**Test DOCX Generation:**
```bash
curl -X POST "http://localhost:8000/api/resume-builder/generate-docx" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "course": "Computer Science",
    "education_background": "BS Computer Science, Test University",
    "skills": "Python, JavaScript",
    "internship_experience": "Software Intern at Test Company",
    "additional_info": "Dean List"
  }' \
  --output test_resume.docx
```

---

## Important Notes

1. **CORS Headers:** Make sure your FastAPI backend has CORS configured to allow requests from your Bubble.io domain

2. **File Download in Bubble:** The API returns a file directly. Bubble should automatically handle the download when you use the "Download file" action

3. **Error Handling:** Add error handling in your Bubble workflow to show messages if the API call fails

4. **Authentication:** If your API requires authentication, add the auth token in the API Connector headers

5. **Backend URL:** Replace `https://your-backend-url.com` with your actual deployed backend URL

---

## Deployment Checklist

- [ ] Install `reportlab` library: `pip install reportlab`
- [ ] Update requirements.txt with `reportlab`
- [ ] Deploy backend with new endpoints
- [ ] Test endpoints with cURL
- [ ] Configure API Connector in Bubble
- [ ] Create download buttons in Bubble UI
- [ ] Test end-to-end flow
- [ ] Verify CORS settings

---

## Troubleshooting

**Issue:** File doesn't download in Bubble
- **Solution:** Check that the API response content-type is correct and Bubble's "Download file" action is configured

**Issue:** CORS error
- **Solution:** Add your Bubble.io domain to the CORS allowed origins in FastAPI

**Issue:** PDF/DOCX formatting issues
- **Solution:** The resume text formatting affects the output. Ensure the AI generates well-structured text

**Issue:** 500 error
- **Solution:** Check backend logs for specific error. May need to install missing dependencies
