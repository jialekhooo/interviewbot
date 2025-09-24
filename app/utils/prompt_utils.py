import os
from typing import Dict, Any

def load_prompt(template_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = os.path.join(os.path.dirname(__file__), "..", "prompts", f"{template_name}.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt template '{template_name}' not found at {path}")

def fill_prompt(template_name: str, **kwargs) -> str:
    """Load a prompt template and fill in the placeholders with provided values."""
    prompt = load_prompt(template_name)
    for key, value in kwargs.items():
        placeholder = "{" + key + "}"
        prompt = prompt.replace(placeholder, str(value))
    return prompt

def validate_prompt_variables(template_name: str, **kwargs) -> bool:
    """Check if all required variables are provided for a template."""
    prompt = load_prompt(template_name)
    
    # Find all placeholders in the template
    import re
    placeholders = re.findall(r'\{(\w+)\}', prompt)
    
    # Check if all placeholders have corresponding kwargs
    missing_vars = [var for var in placeholders if var not in kwargs]
    
    if missing_vars:
        raise ValueError(f"Missing required variables for template '{template_name}': {missing_vars}")
    
    return True

# Available prompt templates
AVAILABLE_PROMPTS = [
    "answer_guidance",
    "interview_questions", 
    "mock_interview_scoring",
    "resume_improvement",
    "resume_parsing"
]
