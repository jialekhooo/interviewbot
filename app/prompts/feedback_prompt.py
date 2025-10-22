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
3. Provide a summary of the candidate’s suitability for the role on interview performance.
4. For each interview question:
    - Provide the **sample answer** for interview with more than 2 sentences.
5. Structure the output in a single JSON object with keys:
   {{
       "final_feedback": "Provide the final feedback based on the candidate’s performance",
       "strengths": "Highlight key strengths in interview",
       "areas_for_improvement": "Mention areas where the candidate can improve on answering interview questions",
       "overall_assessment": "Summarize critically the candidate's suitability for the role",
       "sample_answers": [
            "Sample answer based on candidate's experience and Question 1",
            "Sample answer based on candidate's experience and Question 2",
            // Continue for all other questions
       ]
   }}
5. No extra text should be included in the output, only JSON.
"""
    return prompt
