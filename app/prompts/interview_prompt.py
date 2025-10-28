# prompt/feedback_prompt.py

def generate_interview_prompt_text(
    resume: str = "",
    job_description: str = "",
    past_conversations: str = "",
    position: str = "",
    first: bool = False
) -> str:
    """
    Generates a text-based interview prompt with JSON output format.
    """
    if not first:
        question = f"2. Generate ONE interview question likely to be asked."
    else:
        question = "2. Generate ONE question to introduce the candidate"

    prompt = f"""
You are a professional interviewer. The candidate has the following resume:

{resume or "— No resume provided —"}

Position:
{position or "--- Not specified ---"}

The job description is:

{job_description or "— No job description provided —"}

Past Conversations:

{past_conversations or "— No previous conversation —"}

Question Types:
Behavioral, Technical, System Design, Algorithm, Cultural Fit, Case Study

Instructions:
1.Based on the job description and past conversations, choose the difficulty level and question types of the interview.
{question}
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