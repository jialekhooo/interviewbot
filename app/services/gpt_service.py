import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GPTService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def call_gpt(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> Dict[str, Any]:
        """Call OpenAI GPT model with a given prompt and return JSON output if possible."""
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
        return {
            "raw_output": f"Mocked GPT response to: '{prompt}'"
        }

    def call_gpt_with_system(self, system_prompt: str, user_prompt: str, model: str = None, temperature: float = 0.7):
        questions = [
            "Tell me about yourself.",
            "What are your strengths and weaknesses?",
            "Describe a challenging project you worked on.",
            "How do you stay up to date with industry trends?",
            "Why do you want this job?"
        ]
        return {
            "raw_output": random.choice(questions)
        }

# Global instance
gpt_service = FakeGPTService()
