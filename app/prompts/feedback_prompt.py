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
4. For EACH of the 5 interview questions asked in the past conversations:
    - STEP 1: CAREFULLY READ the EXACT question that was asked word-by-word
    - STEP 2: IDENTIFY the KEY TOPIC of the question (e.g., "leadership from NS", "learning new technology", "managing events", "teamwork")
    - STEP 3: Find experiences from the candidate's resume that DIRECTLY relate to that KEY TOPIC
    - STEP 4: Craft a sample answer that EXPLICITLY addresses the question using those relevant experiences
    - Each sample answer MUST demonstrate the STAR method (Situation, Task, Action, Result)
    - The sample answer MUST use the SAME KEYWORDS from the question (e.g., if question mentions "leadership from NS", answer must mention NS leadership experience)
    - DO NOT use random unrelated experiences from the resume
    - DO NOT reuse the same example for multiple questions
    
    CRITICAL EXAMPLES:
    ❌ WRONG: Question asks about "leadership from NS" → Answer talks about "Financial Controller budget planning"
    ✅ CORRECT: Question asks about "leadership from NS" → Answer talks about "Platoon Sergeant leading team in NS"
    
    ❌ WRONG: Question asks about "learning new programming language" → Answer talks about "National Service operations"
    ✅ CORRECT: Question asks about "learning new programming language" → Answer talks about "Learning React for internship project"
    
    ❌ WRONG: Question asks about "managing events and diverse teams" → Answer talks about "Welfare Manager team bonding"
    ✅ CORRECT: Question asks about "managing events and diverse teams" → Answer talks about "Organizing NTU Hall events with diverse committee members"
5. Structure the output in a single JSON object with keys:
   {{
       "final_feedback": "Provide the final feedback based on the candidate's performance",
       "strengths": "Highlight key strengths in interview",
       "areas_for_improvement": "Mention areas where the candidate can improve on answering interview questions",
       "overall_assessment": "Summarize critically the candidate's suitability for the role",
       "sample_answer_1": "Detailed sample answer for Question 1 using STAR method that DIRECTLY answers Question 1 (DO NOT include 'Sample Answer:' label, just provide the answer text)",
       "sample_answer_2": "Detailed sample answer for Question 2 using STAR method that DIRECTLY answers Question 2 (DO NOT include 'Sample Answer:' label, just provide the answer text)",
       "sample_answer_3": "Detailed sample answer for Question 3 using STAR method that DIRECTLY answers Question 3 (DO NOT include 'Sample Answer:' label, just provide the answer text)",
       "sample_answer_4": "Detailed sample answer for Question 4 using STAR method that DIRECTLY answers Question 4 (DO NOT include 'Sample Answer:' label, just provide the answer text)",
       "sample_answer_5": "Detailed sample answer for Question 5 using STAR method that DIRECTLY answers Question 5 (DO NOT include 'Sample Answer:' label, just provide the answer text)"
   }}
6. CRITICAL REQUIREMENTS: 
   - You MUST provide all 5 sample_answer fields (sample_answer_1 through sample_answer_5)
   - Each sample answer MUST be relevant to its corresponding question
   - DO NOT give generic answers or reuse the same story for different questions
   - MATCH THE KEYWORDS: If the question mentions "National Service", your answer MUST mention National Service
   - MATCH THE KEYWORDS: If the question mentions "leadership", your answer MUST demonstrate leadership
   - MATCH THE KEYWORDS: If the question mentions "events", your answer MUST be about organizing/managing events
   - MATCH THE KEYWORDS: If the question mentions "learning new technology", your answer MUST be about learning a new technology
   - READ THE QUESTION CAREFULLY before selecting which resume experience to use
7. VERIFICATION STEP:
   - Before finalizing each sample answer, ask yourself: "Does this answer DIRECTLY address what the question is asking?"
   - If NO, find a different experience from the resume that better matches the question
8. FORMATTING REQUIREMENTS:
   - DO NOT include labels like "Sample Answer:", "**Sample Answer:**", or any prefixes in the sample_answer fields
   - Start directly with the answer content (e.g., "During my time at...", "In my role as...", etc.)
   - The sample answer should be plain text without any markdown formatting like ** or ##
9. No extra text should be included in the output, only JSON.
"""
    return prompt
