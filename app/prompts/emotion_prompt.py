# prompt.py
import os, json, base64
from typing import List, Tuple
from openai import OpenAI

MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")  # multimodal-capable (gpt-4o, gpt-4o-mini, or gpt-4-turbo)

RUBRIC = """
You are an interview coach evaluating professionalism from visuals only (silent video).
Score 0–100 overall using:
- Composure (25%)
- Eye contact (20%)
- Smile (15%)
- Listening cues (15%)
- Posture (15%)
- Distractions (10%)
Be fair to cultural and accessibility differences; if visibility is poor, note uncertainty.
Ensure the field below is a JSON object with the following keys, every key MUST have a value.
"recommendations
Return strict JSON:
{
  "overall": 0-100,
  "subscores": {
    "composure": 0-100,
    "eye_contact": 0-100,
    "smile": 0-100,
    "listening": 0-100,
    "posture": 0-100,
    "distractions": 0-100
  },
  "notes": "one short paragraph",
  "recommendations": ["tip1","tip2","tip3"]
}
"""

_client = None
def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client

def score_professionalism_from_images(images: List[bytes]) -> Tuple[int, dict]:
    """
    Score professionalism from video frames using OpenAI Vision API.
    Returns overall score (0-100) and detailed analysis.
    """
    if not images:
        raise ValueError("No images provided for analysis")
    
    content = [{"type": "text", "text": RUBRIC}]
    for b in images:
        uri = "data:image/jpeg;base64," + base64.b64encode(b).decode("utf-8")
        content.append({"type": "image_url", "image_url": {"url": uri}})
    
    client = get_client()
    
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Evaluate visual professionalism from images only. Return ONLY valid JSON, no other text."},
                {"role": "user", "content": content}
            ],
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        raw = completion.choices[0].message.content
        
        # Try to parse JSON
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            s, e = raw.find("{"), raw.rfind("}")
            if s == -1 or e == -1:
                raise ValueError(f"No valid JSON found in response: {raw[:200]}")
            payload = json.loads(raw[s:e+1])
        
        # Validate required fields
        if "overall" not in payload:
            raise ValueError(f"Missing 'overall' field in response: {payload}")
        
        overall = int(payload.get("overall", 0))
        
        # Ensure all required fields exist
        if "subscores" not in payload:
            payload["subscores"] = {}
        if "notes" not in payload:
            payload["notes"] = "Analysis completed"
        if "recommendations" not in payload:
            payload["recommendations"] = []
        
        return overall, payload
        
    except Exception as e:
        # Return error details for debugging
        raise RuntimeError(f"Professionalism scoring failed: {str(e)}")
