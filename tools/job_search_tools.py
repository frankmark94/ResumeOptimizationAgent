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
def save_manual_job_description(
    job_description: str,
    job_title: str = "",
    company_name: str = ""
) -> str:
    """
    Save a manually provided job description to the session for document generation.

    Use this tool when the user pastes or provides a job description directly
    (not from a search). This allows generating resumes/cover letters for ANY job,
    not just those from search results.

    Args:
        job_description: The full job description text provided by the user
        job_title: Job title (optional, will be extracted if not provided)
        company_name: Company name (optional, will be extracted if not provided)

    Returns:
        JSON string with the saved job's ID and details

    Example:
        save_manual_job_description("We are looking for a Senior Python Developer...", "Senior Python Developer", "Acme Corp")
    """
    try:
        import hashlib
        from datetime import datetime
        from models.schemas import JobPosting, RemoteType

        session = get_session()

        # Generate unique job ID from description hash
        job_id = hashlib.md5(job_description.encode()).hexdigest()[:12]

        # Extract title and company if not provided (basic extraction)
        if not job_title:
            # Try to extract from first line or first sentence
            first_line = job_description.split('\n')[0].strip()
            job_title = first_line[:100] if first_line else "Manual Job Entry"

        if not company_name:
            company_name = "User Provided Company"

        # Determine remote type from description
        description_lower = job_description.lower()
        if 'remote' in description_lower and 'hybrid' not in description_lower:
            remote_type = RemoteType.REMOTE
        elif 'hybrid' in description_lower:
            remote_type = RemoteType.HYBRID
        else:
            remote_type = RemoteType.ONSITE

        # Create JobPosting object
        job = JobPosting(
            id=job_id,
            title=job_title,
            company=company_name,
            location="Location Not Specified",
            description=job_description,
            remote_type=remote_type,
            url="",
            salary_range=None,
            posted_date=datetime.now()
        )

        # Calculate match score if resume available
        if session.resume_parsed_data:
            from services.job_search_service import job_search_service
            jobs_with_scores = job_search_service.rank_jobs([job], session.resume_parsed_data)
            job = jobs_with_scores[0]

        # Add to session (prepend so it's first in list)
        if not session.current_job_search_results:
            session.current_job_search_results = []

        # Remove if already exists (avoid duplicates)
        session.current_job_search_results = [
            j for j in session.current_job_search_results if j.id != job_id
        ]

        # Add to beginning of list
        session.current_job_search_results.insert(0, job)
        session.selected_job_id = job_id
        session.add_to_summary(f"Saved manual job: {job_title} at {company_name}")

        result = {
            "status": "success",
            "message": f"Job description saved successfully for '{job_title}' at {company_name}",
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "remote_type": job.remote_type.value,
                "match_score": job.match_score,
                "description_length": len(job_description)
            },
            "instruction": "You can now use this job_id to generate optimized resumes or cover letters."
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error saving manual job description: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Error saving job description: {str(e)}"
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
