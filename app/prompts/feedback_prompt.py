def generate_final_feedback_prompt_text(
    resume: str = "",
    job_description: str = "",
    past_conversations: str = "",
    position: str = ""
) -> str:
    """
    Generates a final feedback interview prompt with JSON output format.
    """

    prompt = f"""
You are a professional interviewer. The candidate has the following resume:

{resume or "— No resume provided —"}

The job description is:

{job_description or "— No job description provided —"}

Position: {position or "— Not specified —"}

Past Conversations:

{past_conversations or "— No previous conversation —"}

Instructions:
1. Based on the candidate's performance throughout the interview, provide **final feedback** on interview performance.
2. Assess the candidate's strengths and areas for improvement on interview performance.
3. Provide a summary of the candidate's suitability for the role on interview performance.
4. For EACH of the 5 interview questions asked:
    - Provide a **detailed sample answer** (minimum 3-4 sentences) based on the candidate's resume and experience
    - Each sample answer should demonstrate the STAR method (Situation, Task, Action, Result)
    - Tailor the answer to the specific question and the candidate's background
5. Structure the output in a single JSON object with keys:
   {{
       "final_feedback": "Provide the final feedback based on the candidate's performance",
       "strengths": "Highlight key strengths in interview",
       "areas_for_improvement": "Mention areas where the candidate can improve on answering interview questions",
       "overall_assessment": "Summarize critically the candidate's suitability for the role",
       "sample_answer_1": "Detailed sample answer for Question 1 using STAR method (3-4 sentences minimum)",
       "sample_answer_2": "Detailed sample answer for Question 2 using STAR method (3-4 sentences minimum)",
       "sample_answer_3": "Detailed sample answer for Question 3 using STAR method (3-4 sentences minimum)",
       "sample_answer_4": "Detailed sample answer for Question 4 using STAR method (3-4 sentences minimum)",
       "sample_answer_5": "Detailed sample answer for Question 5 using STAR method (3-4 sentences minimum)"
   }}
6. CRITICAL: You MUST provide all 5 sample_answer fields (sample_answer_1 through sample_answer_5).
7. No extra text should be included in the output, only JSON.
"""
    return prompt
