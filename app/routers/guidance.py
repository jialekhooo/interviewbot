from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from ..services.gpt_service import gpt_service
from ..utils.prompt_utils import fill_prompt

router = APIRouter()

class GuidanceRequest(BaseModel):
    question: str
    user_answer: str
    context: str = ""

class GuidanceResponse(BaseModel):
    guidance: str
    improved_answer: str
    score: float
    feedback: Dict[str, Any]

@router.post("/answer", response_model=GuidanceResponse)
async def get_answer_guidance(request: GuidanceRequest):
    """
    Provide guidance on how to improve an interview answer
    """
    try:
        # Use the answer guidance prompt template
        prompt = fill_prompt(
            "answer_guidance",
            question=request.question,
            user_answer=request.user_answer,
            context=request.context
        )
        
        result = gpt_service.call_gpt(prompt, temperature=0.7)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"AI service error: {result['error']}")
        
        # Parse the response or use raw output
        if "raw_output" in result:
            guidance_text = result["raw_output"]
            return GuidanceResponse(
                guidance=guidance_text,
                improved_answer="See guidance above for improvement suggestions",
                score=0.7,
                feedback={"raw_response": guidance_text}
            )
        
        # If structured response
        return GuidanceResponse(
            guidance=result.get("guidance", "No specific guidance provided"),
            improved_answer=result.get("improved_answer", "See guidance for suggestions"),
            score=result.get("score", 0.7),
            feedback=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate guidance: {str(e)}")

@router.get("/health")
async def guidance_health():
    """Health check for guidance service"""
    return {"status": "ok", "service": "guidance"}
