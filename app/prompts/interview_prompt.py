# prompt/feedback_prompt.py

def generate_interview_prompt_text(
    resume: str = "",
    job_description: str = "",
    past_conversations: str = "",
    position: str = "",
    difficulty: str = "Medium",
    question_type: str = "General"
) -> str:
    """
    Generates a text-based interview prompt with JSON output format.
    """

    prompt = f"""
You are a professional interviewer. The candidate has the following resume:

{resume or "— No resume provided —"}

The job description is:

{job_description or "— No job description provided —"}

Position: {position or "— Not specified —"}
Difficulty: {difficulty or "Medium"}

Past Conversations:

{past_conversations or "— No previous conversation —"}

Instructions:
1. Generate ONE {question_type} interview question likely to be asked.
2. If no past_conversations are provided, generate a question to introduce the candidate.
3. Provide a sample answer for each question based on the candidate's experience.
4. Structure the output in a single JSON object with keys:
   {{
       "question": "the interview question",
       "sample_answer": "a sample answer based on the candidate",
   }}
5. No extra text should be included in the output, only JSON.
6. Prevent from repeating the same question.
"""
    return prompt