"""Resume and job comparison tool for gap analysis."""
import json
from typing import Dict, List, Set
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from config import settings


def calculate_skill_match(resume_skills: List[str], job_requirements: List[str]) -> Dict:
    """Calculate skill matching between resume and job requirements."""
    resume_skills_lower = {skill.lower().strip() for skill in resume_skills if skill}
    job_requirements_lower = {req.lower().strip() for req in job_requirements if req}

    # Exact matches
    matching = resume_skills_lower.intersection(job_requirements_lower)

    # Missing skills
    missing = job_requirements_lower - resume_skills_lower

    # Partial matches (substring matching)
    partial = set()
    for job_skill in job_requirements_lower:
        for resume_skill in resume_skills_lower:
            if (job_skill in resume_skill or resume_skill in job_skill) and job_skill not in matching:
                partial.add(job_skill)

    missing = missing - partial

    # Calculate percentages
    total_required = len(job_requirements_lower)
    match_score = (len(matching) + len(partial) * 0.5) / total_required * 100 if total_required > 0 else 0

    return {
        "matching_skills": list(matching),
        "missing_skills": list(missing),
        "partial_matches": list(partial),
        "match_score": round(match_score, 2),
        "total_required": total_required,
        "total_matched": len(matching)
    }


async def compare_with_llm(resume_json: str, job_analysis_json: str) -> Dict:
    """Use Claude to perform detailed comparison and gap analysis."""
    llm = ChatAnthropic(
        model=settings.model_name,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.3
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert career advisor and resume analyst.

        Compare the candidate's resume against the job requirements and provide detailed gap analysis.

        Return a JSON object with:
        - overall_fit: A score from 0-100 indicating how well the resume matches the job
        - strengths: List of candidate's strong points that align with the job
        - gaps: List of specific skills/experiences the candidate is missing
        - recommendations: Specific suggestions for how to improve the match
        - experience_level_match: Whether the candidate's experience level matches (true/false)
        - keywords_to_add: Technical keywords from the job that should be in the resume

        Be specific and actionable in your analysis."""),
        ("human", """Resume Data:
{resume}

Job Requirements:
{job}

Please provide a detailed comparison and gap analysis.""")
    ])

    chain = prompt | llm
    response = await chain.ainvoke({
        "resume": resume_json,
        "job": job_analysis_json
    })

    # Parse response
    try:
        content = response.content
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            result = {
                "overall_fit": 0,
                "strengths": [],
                "gaps": [],
                "recommendations": [],
                "experience_level_match": False,
                "keywords_to_add": [],
                "raw_analysis": content
            }
    except Exception as e:
        result = {
            "error": f"Failed to parse analysis: {str(e)}",
            "raw_content": content
        }

    return result


@tool
def compare_resume_to_job(resume_json: str, job_analysis_json: str) -> str:
    """
    Compare a resume against a job's requirements to identify gaps and matches.

    Args:
        resume_json: JSON string of parsed resume data (from parse_resume tool)
        job_analysis_json: JSON string of job analysis (from analyze_job_description tool)

    Returns:
        JSON string containing:
        - match_score: Overall percentage match (0-100)
        - matching_skills: Skills the candidate has that match requirements
        - missing_skills: Required skills the candidate lacks
        - partial_matches: Skills that partially match
        - overall_fit: LLM assessment of fit (0-100)
        - strengths: Candidate's strong points
        - gaps: Specific areas for improvement
        - recommendations: Actionable suggestions
        - keywords_to_add: Keywords to include in resume
    """
    try:
        # Parse inputs
        resume_data = json.loads(resume_json)
        job_data = json.loads(job_analysis_json)

        if "error" in resume_data:
            return json.dumps({"error": f"Invalid resume data: {resume_data['error']}"})

        if "error" in job_data:
            return json.dumps({"error": f"Invalid job data: {job_data['error']}"})

        # Extract skills and requirements
        resume_skills = resume_data.get("skills", [])
        job_requirements = job_data.get("requirements", []) + job_data.get("extracted_keywords", [])

        # Calculate basic skill matching
        skill_match = calculate_skill_match(resume_skills, job_requirements)

        # Use LLM for deeper analysis
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        llm_analysis = loop.run_until_complete(compare_with_llm(resume_json, job_analysis_json))

        # Combine results
        result = {
            **skill_match,
            **llm_analysis,
            "analysis_complete": True
        }

        return json.dumps(result, indent=2)

    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Invalid JSON input: {str(e)}"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Failed to compare resume to job: {str(e)}"
        })


@tool
def calculate_match_score(resume_skills: str, job_keywords: str) -> str:
    """
    Calculate a simple match score between resume skills and job keywords.

    Args:
        resume_skills: Comma-separated list of skills from resume
        job_keywords: Comma-separated list of keywords from job posting

    Returns:
        JSON string with match score and breakdown
    """
    try:
        skills_list = [s.strip() for s in resume_skills.split(',') if s.strip()]
        keywords_list = [k.strip() for k in job_keywords.split(',') if k.strip()]

        result = calculate_skill_match(skills_list, keywords_list)

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to calculate match score: {str(e)}"
        })
