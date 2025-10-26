import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GPTService:
    def __init__(self):
        # Do NOT create the OpenAI client at import time to avoid startup crashes
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client: Optional[OpenAI] = None

    def _ensure_client(self) -> bool:
        """Lazily initialize the OpenAI client. Returns True if ready, else False."""
        if self.client is not None:
            return True
        if not self.api_key:
            # Avoid crashing; caller can handle missing client
            print("Warning: OPENAI_API_KEY not found; AI features disabled")
            return False
        try:
            self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")
            self.client = None
            return False
    
    def call_gpt(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> Dict[str, Any]:
        """Call OpenAI GPT model with a given prompt and return JSON output if possible."""
        if not self._ensure_client():
            return {"error": "OpenAI client not initialized"}
            
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            content = response.choices[0].message.content
            
            # Try to parse JSON, fallback to raw string
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_output": content, "error": "Failed to parse JSON"}
                
        except Exception as e:
            return {"error": f"OpenAI API call failed: {str(e)}"}
    
    def call_gpt_with_system(self, system_prompt: str, user_prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> Dict[str, Any]:
        """Call OpenAI GPT with system and user prompts."""
        if not self._ensure_client():
            return {"error": "OpenAI client not initialized"}
            
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_output": content, "error": "Failed to parse JSON"}
                
        except Exception as e:
            return {"error": f"OpenAI API call failed: {str(e)}"}

# Global instance
# gpt_service = GPTService()


import random

class FakeGPTService:
    def call_gpt(self, prompt: str, model: str = None, temperature: float = 0.7):
        # Check if this is a resume review request
        if "resume" in prompt.lower() or "suggestions" in prompt.lower():
            feedback = """Here are 5 suggestions to strengthen your resume for tech jobs:

1. **Add More Technical Skills & Certifications**
   - Consider adding certifications like AWS, Azure, or Google Cloud
   - Include specific frameworks and tools you've used (e.g., React, Docker, Kubernetes)
   - List programming languages with proficiency levels

2. **Highlight Soft Skills**
   - Leadership: Mention times you led teams or mentored junior developers
   - Communication: Emphasize cross-functional collaboration
   - Problem-solving: Showcase how you tackled complex technical challenges

3. **Use Strong Action Verbs & Quantifiable Achievements**
   - Replace weak verbs with: "Architected", "Optimized", "Spearheaded", "Implemented"
   - Add metrics: "Reduced load time by 40%", "Increased user engagement by 25%"
   - Show impact: "Saved company $50K annually through automation"

4. **Improve Overall Formatting**
   - Keep it to 1-2 pages maximum
   - Use consistent bullet points and spacing
   - Ensure dates are aligned and formatted uniformly
   - Use a clean, professional font (Arial, Calibri, or similar)

5. **Tailor to Job Description**
   - Mirror keywords from the job posting
   - Prioritize relevant experience at the top
   - Remove or minimize irrelevant positions
   - Align your summary with the role requirements

**Overall Assessment:** Your resume shows strong technical experience, but could benefit from more quantifiable achievements and better formatting consistency."""
            return {"raw_output": feedback}
        
        # For interview questions
        questions = [
            "Tell me about yourself.",
            "What are your strengths and weaknesses?",
            "Describe a challenging project you worked on.",
            "How do you stay up to date with industry trends?",
            "Why do you want this job?"
        ]
        return {"raw_output": random.choice(questions)}

    def call_gpt_with_system(self, system_prompt: str, user_prompt: str, model: str = None, temperature: float = 0.7):
        return self.call_gpt(user_prompt, model, temperature)

# Global instance
gpt_service = GPTService() if os.getenv("OPENAI_API_KEY") else FakeGPTService()
gpt_service = FakeGPTService()
