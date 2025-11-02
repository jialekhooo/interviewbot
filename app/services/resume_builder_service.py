import os
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ResumeBuilderService:
    """Service for generating professional resumes using OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        
    def _ensure_client(self) -> bool:
        """Lazily initialize the OpenAI client"""
        if self.client is not None:
            return True
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found")
            return False
        try:
            self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")
            return False
    
    def generate_resume(
        self,
        name: str,
        course: str,
        education_background: str,
        skills: str,
        internship_experience: str,
        additional_info: str = ""
    ) -> Dict[str, Any]:
        """Generate a professional resume using OpenAI"""
        
        if not self._ensure_client():
            return {"error": "OpenAI client not initialized"}
        
        try:
            system_prompt = """You are a professional resume writer and career coach. 
Your task is to format and enhance ONLY the information provided by the user.

IMPORTANT RULES:
- DO NOT add contact information, address, phone, or email unless provided
- DO NOT add sections the user didn't provide information for
- DO NOT invent experiences, skills, or achievements
- ONLY format, organize, and enhance what the user gave you
- Use professional language and action verbs
- Make bullet points clear and impactful
- Keep it concise and ATS-friendly

Return ONLY these sections based on what was provided:
- Name (as header)
- Professional Summary (brief, based on their course and experience)
- Education (from their education_background)
- Technical Skills (from their skills)
- Professional Experience (from their internship_experience)
- Additional Information (only if provided)

Return the resume in a clean, readable text format."""

            user_prompt = f"""Format this information into a professional resume:

**Name:** {name}
**Course:** {course}
**Education:** {education_background}
**Skills:** {skills}
**Experience:** {internship_experience}
**Additional:** {additional_info if additional_info else "None"}

Format this into a clean resume with proper sections and bullet points. DO NOT add information I didn't provide."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            resume_text = response.choices[0].message.content
            
            # Generate detailed analysis and suggestions
            analysis_prompt = f"""Analyze this resume and provide detailed feedback:

{resume_text}

Provide a comprehensive analysis covering:
1. Overall Assessment - First impression and quality
2. Strengths - What's done well
3. Weaknesses - What needs improvement
4. Missing Elements - What should be added
5. Specific Suggestions - 5-7 actionable improvements

Return as JSON with this structure:
{{
    "overall_score": "X/10",
    "overall_assessment": "brief summary",
    "strengths": ["strength 1", "strength 2", ...],
    "weaknesses": ["weakness 1", "weakness 2", ...],
    "suggestions": ["suggestion 1", "suggestion 2", ...]
}}"""

            analysis_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a resume improvement expert. Provide specific, actionable analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            import json
            analysis_data = json.loads(analysis_response.choices[0].message.content)
            
            return {
                "success": True,
                "resume_text": resume_text,
                "analysis": analysis_data,
                "suggestions": analysis_data.get("suggestions", []),
                "overall_score": analysis_data.get("overall_score", "N/A"),
                "strengths": analysis_data.get("strengths", []),
                "weaknesses": analysis_data.get("weaknesses", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Resume generation failed: {str(e)}"
            }


class FakeResumeBuilderService:
    """Fake service for testing without OpenAI API"""
    
    def generate_resume(
        self,
        name: str,
        course: str,
        education_background: str,
        skills: str,
        internship_experience: str,
        additional_info: str = ""
    ) -> Dict[str, Any]:
        """Generate a mock professional resume"""
        
        # Build additional info section separately to avoid f-string backslash issue
        additional_section = ""
        if additional_info:
            additional_section = f"\nADDITIONAL INFORMATION\n-------------------\n{additional_info}\n"
        
        resume_text = f"""
{name.upper()}
{'=' * len(name)}

PROFESSIONAL SUMMARY
-------------------
Motivated {course} student with a strong foundation in technical and analytical skills. 
Proven ability to apply theoretical knowledge in practical settings through internship experience.

EDUCATION
---------
{education_background}
Course: {course}

TECHNICAL SKILLS
---------------
{skills}

PROFESSIONAL EXPERIENCE
----------------------
{internship_experience}
{additional_section}
ACHIEVEMENTS & INTERESTS
-----------------------
- Strong problem-solving and analytical skills
- Excellent communication and teamwork abilities
- Passionate about continuous learning and professional development
"""

        suggestions = [
            "Add specific GPA or academic achievements to strengthen your education section",
            "Quantify your internship achievements with metrics (e.g., 'Improved efficiency by 20%')",
            "Include relevant coursework or projects that demonstrate your skills",
            "Add certifications or online courses relevant to your field",
            "Consider adding a LinkedIn profile or portfolio link to your contact information"
        ]
        
        return {
            "success": True,
            "resume_text": resume_text.strip(),
            "suggestions": suggestions
        }


# Global instance - use real OpenAI service
# resume_builder_service = FakeResumeBuilderService()  # Fake service for testing
# Use real OpenAI service when API key is available
resume_builder_service = ResumeBuilderService() if os.getenv("OPENAI_API_KEY") else FakeResumeBuilderService()
