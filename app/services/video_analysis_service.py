import os
import base64
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import subprocess

load_dotenv()


class VideoAnalysisService:
    """Service for analyzing video interview recordings using OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client: Optional[OpenAI] = None
        
    def _ensure_client(self) -> bool:
        """Lazily initialize the OpenAI client"""
        if self.client is not None:
            return True
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found; video analysis disabled")
            return False
        try:
            self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")
            return False
    
    def extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """Extract audio from video file using ffmpeg"""
        try:
            audio_path = video_path.rsplit('.', 1)[0] + '.mp3'
            
            # Use ffmpeg to extract audio
            command = [
                'ffmpeg', '-i', video_path,
                '-vn',  # No video
                '-acodec', 'libmp3lame',
                '-q:a', '2',  # Quality
                audio_path,
                '-y'  # Overwrite if exists
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            return audio_path
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper API"""
        if not self._ensure_client():
            return {"error": "OpenAI client not initialized"}
        
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return {
                "transcript": transcript,
                "success": True
            }
        except Exception as e:
            return {
                "error": f"Transcription failed: {str(e)}",
                "success": False
            }
    
    def analyze_interview_response(
        self,
        transcript: str,
        question: str,
        position: str
    ) -> Dict[str, Any]:
        """Analyze interview response using GPT-4"""
        if not self._ensure_client():
            return {"error": "OpenAI client not initialized"}
        
        try:
            system_prompt = f"""You are an expert interview coach analyzing a candidate's video interview response.
The candidate is applying for a {position} position.

Provide a comprehensive analysis in JSON format with the following structure:
{{
    "overall_feedback": "Detailed feedback on the response",
    "scores": {{
        "content_quality": <score 1-10>,
        "clarity": <score 1-10>,
        "confidence": <score 1-10>,
        "relevance": <score 1-10>,
        "structure": <score 1-10>
    }},
    "strengths": ["strength 1", "strength 2", ...],
    "areas_for_improvement": ["area 1", "area 2", ...],
    "specific_suggestions": ["suggestion 1", "suggestion 2", ...],
    "communication_style": "Assessment of communication style",
    "overall_score": <average score 1-10>
}}"""

            user_prompt = f"""Question: {question}

Candidate's Response (transcribed from video):
{transcript}

Please analyze this interview response and provide detailed feedback."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            analysis = json.loads(content)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "success": False
            }
    
    def analyze_video_interview(
        self,
        video_path: str,
        question: str,
        position: str
    ) -> Dict[str, Any]:
        """Complete video interview analysis pipeline"""
        result = {
            "transcript": "",
            "feedback": "",
            "scores": {},
            "analysis": {},
            "success": False
        }
        
        try:
            # Step 1: Extract audio from video
            audio_path = self.extract_audio_from_video(video_path)
            if not audio_path:
                return {
                    **result,
                    "error": "Failed to extract audio from video"
                }
            
            # Step 2: Transcribe audio
            transcription_result = self.transcribe_audio(audio_path)
            if not transcription_result.get("success"):
                return {
                    **result,
                    "error": transcription_result.get("error", "Transcription failed")
                }
            
            transcript = transcription_result["transcript"]
            result["transcript"] = transcript
            
            # Step 3: Analyze the response
            analysis_result = self.analyze_interview_response(
                transcript=transcript,
                question=question,
                position=position
            )
            
            if not analysis_result.get("success"):
                return {
                    **result,
                    "error": analysis_result.get("error", "Analysis failed")
                }
            
            analysis = analysis_result["analysis"]
            result["analysis"] = analysis
            result["feedback"] = analysis.get("overall_feedback", "")
            result["scores"] = analysis.get("scores", {})
            result["success"] = True
            
            # Cleanup audio file
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            return {
                **result,
                "error": f"Video analysis failed: {str(e)}"
            }


class FakeVideoAnalysisService:
    """Fake service for testing without OpenAI API"""
    
    def analyze_video_interview(
        self,
        video_path: str,
        question: str,
        position: str
    ) -> Dict[str, Any]:
        """Return fake analysis results"""
        return {
            "transcript": "This is a sample transcript of the video interview response. The candidate discussed their experience with relevant technologies and demonstrated good communication skills.",
            "feedback": f"""Great job on your video interview response! Here's my detailed feedback:

**Strengths:**
- Clear and confident communication style
- Relevant examples from your experience
- Good structure in your response (situation, action, result)
- Strong technical knowledge for the {position} role

**Areas for Improvement:**
- Could provide more specific metrics and outcomes
- Consider adding more details about your problem-solving process
- Work on maintaining eye contact with the camera
- Reduce filler words like "um" and "uh"

**Overall:** You demonstrated strong potential for the {position} role. With some refinement in delivery and more quantifiable examples, you'll be even more impressive in future interviews.""",
            "scores": {
                "content_quality": 8,
                "clarity": 7,
                "confidence": 8,
                "relevance": 9,
                "structure": 7,
                "overall_score": 7.8
            },
            "analysis": {
                "strengths": [
                    "Clear communication",
                    "Relevant experience",
                    "Good structure"
                ],
                "areas_for_improvement": [
                    "Add more metrics",
                    "Improve eye contact",
                    "Reduce filler words"
                ],
                "specific_suggestions": [
                    "Practice your response with a timer to ensure conciseness",
                    "Record yourself and review to identify areas for improvement",
                    "Prepare STAR method examples for common questions"
                ],
                "communication_style": "Professional and articulate with room for refinement"
            },
            "success": True
        }


# Global instance - use fake service for now
video_analysis_service = FakeVideoAnalysisService()
# Uncomment below to use real OpenAI service when API key is available
# video_analysis_service = VideoAnalysisService() if os.getenv("OPENAI_API_KEY") else FakeVideoAnalysisService()
