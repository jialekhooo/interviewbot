import random
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import os
from dotenv import load_dotenv
from .gpt_service import gpt_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class QuestionType(str, Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    ALGORITHM = "algorithm"
    CULTURE_FIT = "culture_fit"
    CASE_STUDY = "case_study"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class InterviewSimulator:
    """
    A class to simulate interviews and provide feedback.
    """
    
    def __init__(
        self,
        position: str,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        question_types: List[QuestionType] = None,
        resume_data: Dict[str, Any] = None
    ):
        """
        Initialize the InterviewSimulator.
        
        Args:
            position: The job position being interviewed for
            difficulty: The difficulty level of questions
            question_types: List of question types to include
            resume_data: Optional resume data to tailor questions
        """
        self.position = position

        # Coerce difficulty into DifficultyLevel enum
        if isinstance(difficulty, DifficultyLevel):
            self.difficulty = difficulty
        elif isinstance(difficulty, str):
            try:
                self.difficulty = DifficultyLevel(difficulty.lower())
            except Exception:
                self.difficulty = DifficultyLevel.MEDIUM
        else:
            self.difficulty = DifficultyLevel.MEDIUM

        # Coerce question_types into List[QuestionType]
        def _coerce_qtypes(qtypes: Optional[List[Any]]) -> List[QuestionType]:
            if not qtypes:
                return [
                    QuestionType.BEHAVIORAL,
                    QuestionType.TECHNICAL,
                    QuestionType.SYSTEM_DESIGN,
                    QuestionType.CULTURE_FIT,
                ]
            coerced: List[QuestionType] = []
            for qt in qtypes:
                if isinstance(qt, QuestionType):
                    coerced.append(qt)
                elif isinstance(qt, str):
                    val = qt.lower().strip()
                    for enum_val in QuestionType:
                        if enum_val.value == val:
                            coerced.append(enum_val)
                            break
            if not coerced:
                coerced = [QuestionType.BEHAVIORAL, QuestionType.TECHNICAL]
            return coerced

        self.question_types = _coerce_qtypes(question_types)
        self.resume_data = resume_data or {}
        self.questions_asked = []
        self.responses = []
        self.feedback = []
        
        # Load question bank
        self.question_bank = self._load_question_bank()
    
    def _load_question_bank(self) -> Dict[str, List[Dict]]:
        """Load questions from the question bank."""
        # In a real application, this would load from a database or file
        # For now, we'll use a hardcoded set of questions
        return {
            QuestionType.BEHAVIORAL: [
                {
                    "question": "Tell me about a time you faced a difficult challenge and how you overcame it.",
                    "difficulty": DifficultyLevel.EASY,
                    "evaluation_criteria": [
                        "Clear explanation of the situation",
                        "Description of actions taken",
                        "Results achieved",
                        "What was learned"
                    ]
                },
                {
                    "question": "Describe a situation where you had to work with a difficult team member. How did you handle it?",
                    "difficulty": DifficultyLevel.MEDIUM,
                    "evaluation_criteria": [
                        "Conflict resolution skills",
                        "Communication approach",
                        "Emotional intelligence",
                        "Outcome and learning"
                    ]
                },
                {
                    "question": "Tell me about a time you failed and what you learned from it.",
                    "difficulty": DifficultyLevel.MEDIUM,
                    "evaluation_criteria": [
                        "Honesty about failure",
                        "Analysis of what went wrong",
                        "Lessons learned",
                        "How it influenced future behavior"
                    ]
                }
            ],
            QuestionType.TECHNICAL: [
                {
                    "question": "Explain the difference between REST and GraphQL.",
                    "difficulty": DifficultyLevel.EASY,
                    "evaluation_criteria": [
                        "Technical accuracy",
                        "Clarity of explanation",
                        "Use of examples",
                        "Understanding of trade-offs"
                    ]
                },
                {
                    "question": "How would you optimize a slow database query?",
                    "difficulty": DifficultyLevel.MEDIUM,
                    "evaluation_criteria": [
                        "Understanding of database optimization",
                        "Knowledge of indexing",
                        "Query analysis approach",
                        "Performance considerations"
                    ]
                },
                {
                    "question": "Explain how you would design a scalable microservices architecture.",
                    "difficulty": DifficultyLevel.HARD,
                    "evaluation_criteria": [
                        "Understanding of microservices",
                        "Scalability considerations",
                        "Service communication",
                        "Data consistency"
                    ]
                }
            ],
            QuestionType.SYSTEM_DESIGN: [
                {
                    "question": "Design a URL shortening service like bit.ly.",
                    "difficulty": DifficultyLevel.MEDIUM,
                    "evaluation_criteria": [
                        "System requirements clarification",
                        "High-level design",
                        "API design",
                        "Database schema",
                        "Scalability considerations"
                    ]
                },
                {
                    "question": "Design a distributed key-value store like Redis.",
                    "difficulty": DifficultyLevel.HARD,
                    "evaluation_criteria": [
                        "Data partitioning",
                        "Consistency model",
                        "Fault tolerance",
                        "Performance optimization"
                    ]
                }
            ],
            QuestionType.CULTURE_FIT: [
                {
                    "question": "What type of work environment do you thrive in?",
                    "difficulty": DifficultyLevel.EASY,
                    "evaluation_criteria": [
                        "Self-awareness",
                        "Alignment with company culture",
                        "Honesty and authenticity"
                    ]
                },
                {
                    "question": "How do you handle disagreements with your manager?",
                    "difficulty": DifficultyLevel.MEDIUM,
                    "evaluation_criteria": [
                        "Communication skills",
                        "Professionalism",
                        "Conflict resolution approach"
                    ]
                }
            ]
        }
    
    def generate_question(self, question_type: Optional[QuestionType] = None) -> Dict[str, Any]:
        """
        Generate an interview question.
        
        Args:
            question_type: Optional specific type of question to generate
            
        Returns:
            Dictionary containing question details
        """
        if not question_type:
            # Randomly select a question type if not specified
            question_type = random.choice(self.question_types)
        elif isinstance(question_type, str):
            # Coerce incoming string to enum
            try:
                question_type = QuestionType(question_type.lower())
            except Exception:
                question_type = random.choice(self.question_types)
        
        # Filter questions by type and difficulty
        available_questions = [
            q for q in self.question_bank.get(question_type, [])
            if q["difficulty"] == self.difficulty
        ]
        
        if not available_questions:
            # Fall back to any difficulty if none match exactly
            available_questions = self.question_bank.get(question_type, [])
        
        if not available_questions:
            # Fall back to any question type if none available for requested type
            for qt in self.question_types:
                available_questions = self.question_bank.get(qt, [])
                if available_questions:
                    break
        
        if not available_questions:
            raise ValueError("No questions available in the question bank")
        
        # Select a random question
        question_data = random.choice(available_questions)
        
        # Generate a unique question ID
        question_id = f"q_{len(self.questions_asked) + 1}_{datetime.utcnow().timestamp()}"
        
        # Format the question
        question = {
            "question_id": question_id,
            "text": question_data["question"],
            "question_type": question_type.value,
            "difficulty": question_data["difficulty"].value,
            "category": question_type.value,
            "time_limit": 180,  # 3 minutes by default
            "evaluation_criteria": question_data.get("evaluation_criteria", []),
            "keywords": [],
            "follow_up_questions": []
        }
        
        # Store the question
        self.questions_asked.append(question)
        
        return question
    
    def analyze_response(
        self,
        question: Dict[str, Any],
        user_response: str,
        time_taken: Optional[float] = None,
        confidence_level: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Analyze the user's response to an interview question.
        
        Args:
            question: The question that was asked
            user_response: The user's response
            time_taken: Time taken to respond in seconds
            confidence_level: User's self-assessed confidence level (0-1)
            
        Returns:
            Dictionary containing analysis and feedback
        """
        try:
            # Use OpenAI (via gpt_service) to analyze the response
            prompt = self._create_analysis_prompt(question, user_response)

            result = gpt_service.call_gpt_with_system(
                system_prompt="You are an experienced technical interviewer providing detailed feedback on interview responses.",
                user_prompt=prompt,
                temperature=0.7,
            )

            # Handle errors or raw outputs gracefully
            if isinstance(result, dict) and "error" in result:
                raise RuntimeError(result.get("error", "Unknown AI service error"))

            if isinstance(result, dict) and "raw_output" in result:
                feedback_text = result["raw_output"]
                feedback_data = self._parse_feedback(feedback_text)
            elif isinstance(result, dict):
                # If the model returned already-parsed JSON
                feedback_data = result
            else:
                # Fallback to string parsing
                feedback_data = self._parse_feedback(str(result))
            
            # Add metadata
            feedback_data.update({
                "question_id": question["question_id"],
                "question_text": question["text"],
                "user_response": user_response,
                "time_taken": time_taken,
                "confidence_level": confidence_level,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Store the feedback
            self.feedback.append(feedback_data)
            
            return feedback_data
            
        except Exception as e:
            logger.error(f"Error analyzing response: {str(e)}")
            return {
                "error": f"Failed to analyze response: {str(e)}",
                "question_id": question.get("question_id", "unknown"),
                "user_response": user_response
            }
    
    def _create_analysis_prompt(self, question: Dict[str, Any], user_response: str) -> str:
        """Create a prompt for analyzing the user's response."""
        prompt = f"""
        Please analyze the following interview response and provide detailed feedback.
        
        Position: {self.position}
        Question Type: {question['question_type']}
        Difficulty: {question['difficulty']}
        
        Question:
        {question['text']}
        
        Evaluation Criteria:
        """
        
        for i, criterion in enumerate(question.get('evaluation_criteria', []), 1):
            prompt += f"{i}. {criterion}\n"
        
        prompt += f"""
        Candidate's Response:
        {user_response}
        
        Please provide feedback in the following JSON format:
        {{
            "strengths": ["list", "of", "strengths"],
            "areas_for_improvement": ["list", "of", "areas for improvement"],
            "score": 0.0-1.0,
            "detailed_feedback": "Detailed feedback on the response",
            "suggested_response": "A well-structured response example"
        }}
        """
        
        return prompt
    
    def _parse_feedback(self, feedback_text: str) -> Dict[str, Any]:
        """Parse the feedback text into a structured format."""
        try:
            # Try to find JSON in the response
            start_idx = feedback_text.find('{')
            end_idx = feedback_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = feedback_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback if no JSON found
                return {
                    "strengths": [],
                    "areas_for_improvement": [],
                    "score": 0.5,
                    "detailed_feedback": feedback_text,
                    "suggested_response": ""
                }
        except json.JSONDecodeError:
            logger.warning("Failed to parse feedback as JSON, falling back to text")
            return {
                "strengths": [],
                "areas_for_improvement": [],
                "score": 0.5,
                "detailed_feedback": feedback_text,
                "suggested_response": ""
            }
    
    def generate_overall_feedback(self) -> Dict[str, Any]:
        """Generate overall feedback for the entire interview."""
        if not self.feedback:
            return {"error": "No feedback available"}
        
        # Calculate average score
        total_score = sum(f.get('score', 0) for f in self.feedback)
        avg_score = total_score / len(self.feedback) if self.feedback else 0
        
        # Aggregate strengths and areas for improvement
        all_strengths = []
        all_improvements = []
        
        for fb in self.feedback:
            all_strengths.extend(fb.get('strengths', []))
            all_improvements.extend(fb.get('areas_for_improvement', []))
        
        # Count occurrences of each strength/improvement
        from collections import Counter
        strength_counts = Counter(all_strengths)
        improvement_counts = Counter(all_improvements)
        
        # Get most common items
        top_strengths = [item[0] for item in strength_counts.most_common(3)]
        top_improvements = [item[0] for item in improvement_counts.most_common(3)]
        
        # Generate summary
        summary = f"""
        Overall, you performed {'very well' if avg_score >= 0.8 else 'well' if avg_score >= 0.6 else 'adequately' if avg_score >= 0.4 else 'below expectations'} in this interview.
        
        Your key strengths include: {', '.join(top_strengths) if top_strengths else 'No specific strengths identified'}.
        
        Areas for improvement include: {', '.join(top_improvements) if top_improvements else 'No specific areas for improvement identified'}.
        
        Your overall score is {avg_score:.1f}/1.0.
        """
        
        return {
            "overall_score": avg_score,
            "strengths": top_strengths,
            "areas_for_improvement": top_improvements,
            "summary": summary.strip(),
            "detailed_feedback": self.feedback
        }
    
    def get_question_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommended questions based on performance."""
        if not self.feedback:
            return []
        
        # Identify weak areas
        weak_areas = []
        for fb in self.feedback:
            if fb.get('score', 0) < 0.5:  # Threshold for weak areas
                weak_areas.append(fb.get('question_type', 'general'))
        
        # Generate recommendations
        recommendations = []
        for area in set(weak_areas):
            # Get questions targeting weak areas
            questions = self.question_bank.get(area, [])
            if questions:
                rec_question = random.choice(questions)
                recommendations.append({
                    "question": rec_question["question"],
                    "type": area,
                    "difficulty": rec_question["difficulty"],
                    "reason": f"Practice more {area.replace('_', ' ')} questions to improve in this area."
                })
        
        return recommendations

# Example usage
if __name__ == "__main__":
    # Initialize the simulator
    simulator = InterviewSimulator(
        position="Senior Software Engineer",
        difficulty=DifficultyLevel.MEDIUM
    )
    
    # Generate a question
    question = simulator.generate_question(QuestionType.BEHAVIORAL)
    print(f"Question: {question['text']}")
    
    # Simulate a response
    user_response = """
    I once had to deal with a difficult team member who wasn't completing their tasks on time.
    I scheduled a one-on-one meeting to understand the issue and offered to help them prioritize their work.
    We set clear expectations and regular check-ins, which improved their performance.
    """
    
    # Analyze the response
    feedback = simulator.analyze_response(question, user_response)
    print("\nFeedback:")
    print(f"Score: {feedback.get('score', 0):.1f}/1.0")
    print(f"Strengths: {', '.join(feedback.get('strengths', []))}")
    print(f"Areas for improvement: {', '.join(feedback.get('areas_for_improvement', []))}")
    print(f"Detailed feedback: {feedback.get('detailed_feedback', '')}")
    
    # Generate overall feedback
    overall = simulator.generate_overall_feedback()
    print("\nOverall Feedback:")
    print(overall.get('summary', ''))
