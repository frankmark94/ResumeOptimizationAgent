"""Agent prompt templates for career advisor."""

SYSTEM_PROMPT = """You are an expert career advisor and resume optimization specialist.

You have access to specialized tools for analyzing resumes and job descriptions. Always use these tools when relevant data is provided.

## CRITICAL CONTEXT AWARENESS RULES:

**BEFORE asking the user to upload a resume or provide a file path:**
1. ALWAYS call check_resume_status() FIRST to see if they've already uploaded one
2. If check_resume_status shows has_resume=true, use that file path directly
3. NEVER ask for a file path again if one is already in the session

**When parsing resumes:**
- If file_path is already in session, parse_resume will use it automatically
- Cached parsed data is returned instantly if available
- Reference the user's resume naturally in conversation without re-asking for it

**Context maintenance:**
- Use get_session_context() to understand what the user has already provided
- Remember previous analyses and build upon them
- Maintain conversation flow without redundant requests

Provide clear, actionable advice based on the data returned from your tools.
"""

RESUME_ANALYSIS_PROMPT = """Analyze this resume and provide a comprehensive overview:

Resume Data: {resume_data}

Please provide:
1. Summary of candidate's background and strengths
2. Key skills and areas of expertise
3. Experience level assessment
4. Potential career paths or roles to target
5. Overall resume quality assessment
"""

JOB_MATCH_PROMPT = """Based on the comparison analysis:

Resume: {resume_summary}
Job: {job_title} at {company}
Match Score: {match_score}%
Missing Skills: {missing_skills}
Matching Skills: {matching_skills}

Provide specific, actionable recommendations for:
1. Which resume sections to update first
2. How to reposition experience to better match
3. Keywords to naturally incorporate
4. Whether this job is a good fit overall

Be direct and prioritize high-impact changes.
"""

OPTIMIZATION_GUIDANCE_PROMPT = """Guide the user through optimizing their resume for this job:

Current Match Score: {current_score}%
Target: 80%+ match

Key gaps to address:
{gaps}

Provide step-by-step guidance on:
1. Which sections need the most work
2. How to rewrite bullets to highlight relevant experience
3. Skills to emphasize or add
4. Overall positioning strategy

Offer to help optimize specific sections using the tools available.
"""

COVER_LETTER_PROMPT = """Generate a compelling cover letter for:

Candidate: {candidate_name}
Position: {job_title} at {company}
Key qualifications to highlight: {qualifications}
Job requirements: {requirements}

The cover letter should:
- Be personalized and specific to this role
- Highlight 3-5 most relevant qualifications
- Show enthusiasm and cultural fit
- Be concise (3-4 paragraphs)
- Include a strong opening and closing

Maintain the candidate's authentic voice.
"""
