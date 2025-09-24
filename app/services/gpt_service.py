import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GPTService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.client = None
                self.default_model = "gpt-4o-mini"
        else:
            print("Warning: OPENAI_API_KEY not found")
            self.client = None
            self.default_model = "gpt-4o-mini"
    
    def call_gpt(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> Dict[str, Any]:
        """Call OpenAI GPT model with a given prompt and return JSON output if possible."""
        if not self.client:
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
        if not self.client:
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
gpt_service = GPTService()
