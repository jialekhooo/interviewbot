# prompt.py
import os, json, base64
from typing import List, Tuple
from openai import OpenAI

MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1")  # multimodal-capable

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
        _client = OpenAI()
    return _client

def score_professionalism_from_images(images: List[bytes]) -> Tuple[int, dict]:
    content = [{"type": "text", "text": RUBRIC}]
    for b in images:
        uri = "data:image/jpeg;base64," + base64.b64encode(b).decode("utf-8")
        content.append({"type": "image_url", "image_url": {"url": uri}})
    client = get_client()
    completion = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Evaluate visual professionalism from images only."},
            {"role": "user", "content": content}
        ]
    )
    raw = completion.choices[0].message.content
    try:
        payload = json.loads(raw)
    except Exception:
        s, e = raw.find("{"), raw.rfind("}")
        payload = json.loads(raw[s:e+1])
    overall = int(payload.get("overall", 0))
    return overall, payload
