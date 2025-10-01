"""Resume optimizer tool for rewriting content to match job requirements."""
import json
from typing import List, Dict
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from config import settings


async def optimize_resume_section_with_llm(
    section_content: str,
    section_type: str,
    job_requirements: List[str],
    missing_keywords: List[str]
) -> Dict:
    """Use Claude to optimize a resume section for a specific job."""
    llm = ChatAnthropic(
        model=settings.model_name,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.7
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume writer and career coach specializing in ATS optimization.

        Your task is to rewrite resume content to better match job requirements while:
        1. Maintaining truthfulness (don't add false information)
        2. Using strong action verbs
        3. Adding quantifiable achievements where possible
        4. Incorporating relevant keywords naturally
        5. Ensuring ATS compatibility
        6. Keeping the candidate's authentic voice

        Return a JSON object with:
        - optimized_text: The rewritten content
        - keywords_added: List of keywords successfully incorporated
        - improvements: List of specific improvements made
        - ats_score: Estimated ATS compatibility score (0-100)
        - notes: Any important notes about the optimization"""),
        ("human", """Section Type: {section_type}

Original Content:
{content}

Job Requirements:
{requirements}

Missing Keywords to Incorporate (if relevant and truthful):
{keywords}

Please optimize this section for the job while maintaining authenticity.""")
    ])

    chain = prompt | llm
    response = await chain.ainvoke({
        "section_type": section_type,
        "content": section_content,
        "requirements": "\n".join(job_requirements),
        "keywords": ", ".join(missing_keywords)
    })

    # Parse response
    try:
        content = response.content
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            # Fallback: treat entire response as optimized text
            result = {
                "optimized_text": content,
                "keywords_added": [],
                "improvements": ["General optimization applied"],
                "ats_score": 75,
                "notes": "Optimization completed"
            }
    except Exception as e:
        result = {
            "error": f"Failed to parse optimization: {str(e)}",
            "raw_content": content
        }

    return result


async def generate_bullet_points(
    job_title: str,
    company: str,
    job_requirements: List[str],
    num_bullets: int = 5
) -> List[str]:
    """Generate achievement-focused bullet points for a role."""
    llm = ChatAnthropic(
        model=settings.model_name,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.8
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume writer. Generate compelling, achievement-focused bullet points for a work experience entry.

        Each bullet should:
        - Start with a strong action verb
        - Include quantifiable results when possible
        - Highlight relevant skills and technologies
        - Be concise (1-2 lines max)
        - Be ATS-friendly

        Return ONLY a JSON array of bullet point strings."""),
        ("human", """Job Title: {title}
Company: {company}
Job Requirements to Address: {requirements}
Number of bullets needed: {num_bullets}

Generate {num_bullets} achievement-focused bullet points.""")
    ])

    chain = prompt | llm
    response = await chain.ainvoke({
        "title": job_title,
        "company": company,
        "requirements": "\n".join(job_requirements[:5]),  # Top 5 requirements
        "num_bullets": num_bullets
    })

    # Parse response
    try:
        content = response.content
        import re
        # Try to extract JSON array
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            bullets = json.loads(json_match.group(0))
        else:
            # Fallback: split by newlines
            bullets = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
    except Exception:
        bullets = [content]  # Fallback to full content

    return bullets[:num_bullets]


@tool
def optimize_resume_section(
    section_content: str,
    section_type: str,
    job_requirements: str,
    missing_keywords: str = ""
) -> str:
    """
    Optimize a resume section to better match job requirements.

    Args:
        section_content: The original text of the resume section to optimize
        section_type: Type of section (e.g., 'summary', 'experience', 'skills')
        job_requirements: Comma-separated list of job requirements
        missing_keywords: Comma-separated list of keywords to incorporate (optional)

    Returns:
        JSON string containing:
        - optimized_text: Rewritten content
        - keywords_added: Keywords successfully incorporated
        - improvements: Specific improvements made
        - ats_score: Estimated ATS compatibility (0-100)
        - original_text: The original content for comparison
    """
    try:
        if not section_content or not section_content.strip():
            return json.dumps({"error": "Section content is empty"})

        requirements_list = [r.strip() for r in job_requirements.split(',') if r.strip()]
        keywords_list = [k.strip() for k in missing_keywords.split(',') if k.strip()] if missing_keywords else []

        # Use async function
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        optimization = loop.run_until_complete(
            optimize_resume_section_with_llm(
                section_content,
                section_type,
                requirements_list,
                keywords_list
            )
        )

        # Add original text for comparison
        optimization["original_text"] = section_content
        optimization["section_type"] = section_type

        return json.dumps(optimization, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to optimize section: {str(e)}"
        })


@tool
def generate_resume_bullets(
    job_title: str,
    company: str,
    job_requirements: str,
    num_bullets: int = 5
) -> str:
    """
    Generate achievement-focused bullet points for a work experience entry.

    Args:
        job_title: The job title/role
        company: Company name
        job_requirements: Comma-separated list of relevant job requirements to address
        num_bullets: Number of bullet points to generate (default: 5)

    Returns:
        JSON string with list of generated bullet points
    """
    try:
        requirements_list = [r.strip() for r in job_requirements.split(',') if r.strip()]

        # Use async function
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        bullets = loop.run_until_complete(
            generate_bullet_points(
                job_title,
                company,
                requirements_list,
                num_bullets
            )
        )

        return json.dumps({
            "bullets": bullets,
            "count": len(bullets),
            "job_title": job_title,
            "company": company
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to generate bullet points: {str(e)}"
        })


@tool
def improve_ats_compatibility(resume_text: str, target_keywords: str) -> str:
    """
    Analyze and improve ATS (Applicant Tracking System) compatibility of resume text.

    Args:
        resume_text: The resume content to analyze
        target_keywords: Comma-separated list of keywords that should be included

    Returns:
        JSON string with:
        - ats_score: Current ATS compatibility score (0-100)
        - keyword_coverage: Percentage of target keywords found
        - missing_keywords: Keywords not found in resume
        - recommendations: Specific improvements for ATS compatibility
    """
    try:
        keywords_list = [k.strip().lower() for k in target_keywords.split(',') if k.strip()]
        resume_lower = resume_text.lower()

        # Check keyword coverage
        found_keywords = [k for k in keywords_list if k in resume_lower]
        missing_keywords = [k for k in keywords_list if k not in resume_lower]

        keyword_coverage = (len(found_keywords) / len(keywords_list) * 100) if keywords_list else 0

        # ATS compatibility checks
        recommendations = []

        # Check for common ATS issues
        if resume_text.count('•') > resume_text.count('\n') * 0.5:
            recommendations.append("Consider using simple bullet points (-) instead of special characters")

        if len(resume_text.split('\n')) < 10:
            recommendations.append("Add more line breaks to improve readability")

        if not any(keyword in resume_lower for keyword in ['experience', 'education', 'skills']):
            recommendations.append("Add clear section headers (Experience, Education, Skills)")

        # Calculate ATS score
        ats_score = min(100, keyword_coverage * 0.6 + (40 if len(recommendations) < 3 else 20))

        result = {
            "ats_score": round(ats_score, 2),
            "keyword_coverage": round(keyword_coverage, 2),
            "keywords_found": found_keywords,
            "missing_keywords": missing_keywords,
            "recommendations": recommendations,
            "total_keywords": len(keywords_list)
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to analyze ATS compatibility: {str(e)}"
        })
