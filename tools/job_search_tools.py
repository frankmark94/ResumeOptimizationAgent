"""
Job Search Tools - Agent tools for searching and filtering job postings
"""
import json
import logging
import asyncio
from langchain.tools import tool
from typing import Optional
from services.job_search_service import job_search_service
from models.schemas import RemoteType
from utils.session_state import get_session

logger = logging.getLogger(__name__)


@tool
def search_jobs_by_criteria(
    query: str,
    location: str = "",
    remote_type: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Search for job postings that match the specified criteria.

    Use this tool when the user asks to find, search, or look for jobs.

    Args:
        query: Job title or keywords (e.g., "Senior Python Engineer", "Data Scientist")
        location: Location string (e.g., "New York", "San Francisco", "Remote")
        remote_type: Filter by work arrangement: "remote", "hybrid", or "onsite"
        limit: Maximum number of results to return (default: 10, max: 20)

    Returns:
        JSON string containing job search results with match scores

    Example:
        search_jobs_by_criteria("Python Developer", "San Francisco", "remote", 5)
    """
    try:
        # Parse remote_type
        remote_filter = None
        if remote_type:
            remote_type_lower = remote_type.lower()
            if remote_type_lower == "remote":
                remote_filter = RemoteType.REMOTE
            elif remote_type_lower == "hybrid":
                remote_filter = RemoteType.HYBRID
            elif remote_type_lower == "onsite":
                remote_filter = RemoteType.ONSITE

        # Get session to check for resume data
        session = get_session()
        resume_data = session.resume_parsed_data or {}

        # Search jobs
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        jobs = loop.run_until_complete(
            job_search_service.search_jobs(
                query=query,
                location=location,
                remote_type=remote_filter,
                limit=min(limit, 20)
            )
        )

        # Rank jobs if resume data available
        if resume_data and jobs:
            jobs = job_search_service.rank_jobs(jobs, resume_data)

        # Store in session
        session.current_job_search_results = jobs
        session.conversation_summary.append(f"Searched for: {query} in {location or 'any location'}")

        # Format results
        if not jobs:
            return json.dumps({
                "status": "no_results",
                "message": f"No jobs found for '{query}' in '{location or 'any location'}'",
                "count": 0
            })

        results = {
            "status": "success",
            "count": len(jobs),
            "query": query,
            "location": location,
            "jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "salary_range": job.salary_range,
                    "remote_type": job.remote_type.value,
                    "url": job.url,
                    "match_score": job.match_score,
                    "description_preview": job.description[:300] + "..." if len(job.description) > 300 else job.description
                }
                for job in jobs
            ]
        }

        return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Job search error: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Error searching for jobs: {str(e)}"
        })


@tool
def get_job_details(job_id: str) -> str:
    """
    Get full details of a specific job posting by ID.

    Use this tool when the user wants more information about a specific job.

    Args:
        job_id: The job ID from search results

    Returns:
        JSON string with complete job details

    Example:
        get_job_details("12345")
    """
    try:
        session = get_session()
        cached_jobs = session.current_job_search_results or []

        job = job_search_service.get_job_by_id(job_id, cached_jobs)

        if not job:
            return json.dumps({
                "status": "not_found",
                "message": f"Job ID {job_id} not found in current search results"
            })

        # Store selected job in session
        session.selected_job_id = job_id

        result = {
            "status": "success",
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "salary_range": job.salary_range,
                "remote_type": job.remote_type.value,
                "url": job.url,
                "posted_date": job.posted_date.isoformat() if job.posted_date else None,
                "description": job.description,
                "match_score": job.match_score
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error getting job details: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Error retrieving job details: {str(e)}"
        })


@tool
def filter_jobs_by_requirements(
    min_match_score: int = 0,
    remote_only: bool = False,
    has_salary: bool = False
) -> str:
    """
    Filter current job search results by additional criteria.

    Use this tool to narrow down search results based on specific requirements.

    Args:
        min_match_score: Minimum match score (0-100)
        remote_only: Only show remote jobs
        has_salary: Only show jobs with salary information

    Returns:
        JSON string with filtered job results

    Example:
        filter_jobs_by_requirements(min_match_score=70, remote_only=True)
    """
    try:
        session = get_session()
        jobs = session.current_job_search_results or []

        if not jobs:
            return json.dumps({
                "status": "no_results",
                "message": "No jobs to filter. Please search for jobs first."
            })

        # Apply filters
        filtered_jobs = jobs

        if min_match_score > 0:
            filtered_jobs = [j for j in filtered_jobs if (j.match_score or 0) >= min_match_score]

        if remote_only:
            filtered_jobs = [j for j in filtered_jobs if j.remote_type == RemoteType.REMOTE]

        if has_salary:
            filtered_jobs = [j for j in filtered_jobs if j.salary_range is not None]

        # Update session
        session.current_job_search_results = filtered_jobs

        result = {
            "status": "success",
            "count": len(filtered_jobs),
            "filtered_from": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "salary_range": job.salary_range,
                    "remote_type": job.remote_type.value,
                    "match_score": job.match_score
                }
                for job in filtered_jobs
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error filtering jobs: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Error filtering jobs: {str(e)}"
        })


@tool
def list_available_jobs() -> str:
    """
    List jobs currently available in the session from previous searches.

    CRITICAL: Use this tool FIRST when user requests document generation without specifying a job.

    Use this tool when:
    - User wants to create a resume but hasn't specified which job
    - You need to show what jobs are available for document generation
    - User asks "what jobs do I have" or "show my saved jobs"
    - BEFORE calling generate_optimized_resume() if you don't have a job_id

    Returns:
        JSON string with jobs in current session, including job IDs and titles

    Example:
        list_available_jobs()
    """
    try:
        session = get_session()
        jobs = session.current_job_search_results or []

        if not jobs:
            return json.dumps({
                "status": "no_jobs",
                "message": "No jobs in current session. User needs to search for jobs first.",
                "suggestion": "Ask user to provide job search criteria (e.g., 'Find Python jobs in NYC') or ask them to paste a job description.",
                "count": 0
            })

        result = {
            "status": "success",
            "count": len(jobs),
            "message": f"Found {len(jobs)} job(s) in current session",
            "jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "match_score": job.match_score,
                    "index": i + 1  # User-friendly numbering
                }
                for i, job in enumerate(jobs)
            ],
            "instruction": "Present these jobs to the user and ask them to select one by number or company name."
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Error listing available jobs: {str(e)}"
        })
