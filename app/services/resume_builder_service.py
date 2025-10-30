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
Your task is to create a well-structured, professional resume based on the information provided.

Format the resume with the following sections:
1. Contact Information & Summary
2. Education
3. Skills
4. Experience (Internships/Work)
5. Additional Information (if provided)

Make the resume:
- Professional and ATS-friendly
- Well-formatted with clear sections
- Action-oriented with strong verbs
- Quantified where possible
- Tailored to highlight the candidate's strengths
- Free of grammatical errors

Return the resume in a clean, readable text format."""

            user_prompt = f"""Please create a professional resume with the following information:

**Name:** {name}

**Course/Field of Study:** {course}

**Education Background:** 
{education_background}

**Skills:** 
{skills}

**Internship/Work Experience:** 
{internship_experience}

**Additional Information:** 
{additional_info if additional_info else "None provided"}

Please create a comprehensive, professional resume that highlights this candidate's qualifications and potential."""

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
            
            # Generate suggestions for improvement
            suggestions_prompt = f"""Based on this resume, provide 3-5 specific suggestions for improvement:

{resume_text}

Focus on:
- Missing information that would strengthen the resume
- Ways to better quantify achievements
- Additional skills or experiences to highlight
- Formatting or structure improvements

Return as a JSON array of strings."""

            suggestions_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a resume improvement expert. Provide specific, actionable suggestions."},
                    {"role": "user", "content": suggestions_prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            import json
            suggestions_data = json.loads(suggestions_response.choices[0].message.content)
            suggestions = suggestions_data.get("suggestions", [])
            
            return {
                "success": True,
                "resume_text": resume_text,
                "suggestions": suggestions
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


# Global instance - use fake service by default for testing
resume_builder_service = FakeResumeBuilderService()
# Uncomment below to use real OpenAI service when API key is available
# resume_builder_service = ResumeBuilderService() if os.getenv("OPENAI_API_KEY") else FakeResumeBuilderService()
