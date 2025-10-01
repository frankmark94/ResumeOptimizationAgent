"""Job analyzer tool for extracting requirements from job descriptions."""
import re
import json
from typing import List
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from config import settings


def extract_keywords(text: str) -> List[str]:
    """Extract technical keywords and skills from job description."""
    # Common technical keywords and patterns
    tech_patterns = [
        r'\b[A-Z][a-z]+(?:\.[a-z]+)+\b',  # e.g., Node.js, Vue.js
        r'\b[A-Z]{2,}\b',  # Acronyms like AWS, SQL, API
        r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|Ruby|Go|Rust|Swift|Kotlin)\b',
        r'\b(?:React|Angular|Vue|Django|Flask|Spring|Express)\b',
        r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins)\b',
    ]

    keywords = set()
    for pattern in tech_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.update(matches)

    return list(keywords)


async def analyze_job_with_llm(description: str) -> dict:
    """Use Claude to analyze job description and extract structured information."""
    llm = ChatAnthropic(
        model=settings.model_name,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.3
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert job analyst. Extract structured information from job descriptions.

        Return a JSON object with:
        - requirements: List of required skills, experience, and qualifications (hard requirements)
        - nice_to_have: List of preferred/nice-to-have skills and qualifications
        - key_responsibilities: List of main job responsibilities
        - experience_level: Entry/Mid/Senior/Lead level
        - extracted_keywords: Technical skills, tools, and technologies mentioned

        Be thorough and specific. Extract concrete skills and requirements."""),
        ("human", "Job Description:\n\n{description}")
    ])

    chain = prompt | llm
    response = await chain.ainvoke({"description": description})

    # Parse response
    try:
        # Claude returns content in message format
        content = response.content
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            # Fallback parsing
            result = {
                "requirements": [],
                "nice_to_have": [],
                "key_responsibilities": [],
                "experience_level": "Not specified",
                "extracted_keywords": extract_keywords(description)
            }
    except Exception as e:
        result = {
            "error": f"Failed to parse LLM response: {str(e)}",
            "raw_content": content
        }

    return result


@tool
def analyze_job_description(job_description: str, job_url: str = None) -> str:
    """
    Analyze a job description to extract requirements, skills, and key information.

    Args:
        job_description: The full text of the job posting
        job_url: Optional URL where the job was found

    Returns:
        JSON string containing:
        - requirements: List of required skills and qualifications
        - nice_to_have: List of preferred qualifications
        - key_responsibilities: Main job duties
        - experience_level: Required experience level
        - extracted_keywords: Technical keywords and skills
    """
    try:
        if not job_description or len(job_description.strip()) < 50:
            return json.dumps({
                "error": "Job description is too short or empty"
            })

        # Use async function with event loop
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        analysis = loop.run_until_complete(analyze_job_with_llm(job_description))

        # Add metadata
        analysis["job_url"] = job_url
        analysis["description_length"] = len(job_description)

        return json.dumps(analysis, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to analyze job description: {str(e)}"
        })


@tool
def extract_job_keywords(job_description: str) -> str:
    """
    Extract technical keywords and skills from a job description.

    Args:
        job_description: The job posting text

    Returns:
        JSON string with list of extracted keywords
    """
    try:
        keywords = extract_keywords(job_description)

        # Additional skill patterns
        skill_words = ['experience', 'knowledge', 'proficiency', 'familiar', 'expertise']
        lines = job_description.split('\n')

        additional_skills = []
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in skill_words):
                # Extract capitalized words that might be tech terms
                words = re.findall(r'\b[A-Z][a-z]+(?:\.[a-z]+)?\b|\b[A-Z]{2,}\b', line)
                additional_skills.extend(words)

        all_keywords = list(set(keywords + additional_skills))

        return json.dumps({
            "keywords": all_keywords,
            "count": len(all_keywords)
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to extract keywords: {str(e)}"
        })
