"""
Job Search Service - Integration with job search APIs (Adzuna, web scraping fallback)
"""
import requests
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.schemas import JobPosting, RemoteType
from config import settings
import json

logger = logging.getLogger(__name__)


class JobSearchService:
    """Service for searching jobs across multiple platforms."""

    def __init__(self):
        self.adzuna_app_id = settings.adzuna_api_id
        self.adzuna_app_key = settings.adzuna_api_key
        self.base_url = "https://api.adzuna.com/v1/api/jobs/us/search/1"

    async def search_jobs(
        self,
        query: str,
        location: str = "",
        remote_type: Optional[RemoteType] = None,
        limit: int = 10,
        country: str = "us"
    ) -> List[JobPosting]:
        """
        Search for jobs using Adzuna API.

        Args:
            query: Search query (job title, keywords)
            location: Location string (e.g., "New York", "San Francisco")
            remote_type: Filter by remote work type
            limit: Maximum number of results
            country: Country code (default: us)

        Returns:
            List of JobPosting objects with match scores
        """
        try:
            # Build Adzuna API request
            params = {
                "app_id": self.adzuna_app_id,
                "app_key": self.adzuna_app_key,
                "results_per_page": limit,
                "what": query,
                "content-type": "application/json"
            }

            if location:
                params["where"] = location

            # Add remote filter if specified
            if remote_type == RemoteType.REMOTE:
                params["what"] = f"{query} remote"

            logger.info(f"Searching Adzuna API: query={query}, location={location}")

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            jobs = []

            for result in data.get("results", []):
                job = self._parse_adzuna_job(result)
                if job:
                    jobs.append(job)

            logger.info(f"Found {len(jobs)} jobs from Adzuna")
            return jobs

        except requests.RequestException as e:
            logger.error(f"Adzuna API error: {str(e)}")
            # TODO: Fallback to web scraping if API fails
            return []
        except Exception as e:
            logger.error(f"Job search error: {str(e)}")
            return []

    def _parse_adzuna_job(self, result: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse Adzuna API response into JobPosting schema."""
        try:
            # Determine remote type from title/description
            title = result.get("title", "")
            description = result.get("description", "")
            remote_type = RemoteType.ONSITE

            if "remote" in title.lower() or "remote" in description.lower():
                remote_type = RemoteType.REMOTE
            elif "hybrid" in title.lower() or "hybrid" in description.lower():
                remote_type = RemoteType.HYBRID

            # Format salary range
            salary_min = result.get("salary_min")
            salary_max = result.get("salary_max")
            salary_range = None
            if salary_min and salary_max:
                salary_range = f"${salary_min:,.0f} - ${salary_max:,.0f}"
            elif salary_min:
                salary_range = f"${salary_min:,.0f}+"

            # Parse posted date
            created = result.get("created")
            posted_date = None
            if created:
                try:
                    posted_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                except:
                    pass

            job = JobPosting(
                id=result.get("id", str(hash(result.get("redirect_url")))),
                title=title,
                company=result.get("company", {}).get("display_name", "Unknown"),
                location=result.get("location", {}).get("display_name", ""),
                salary_range=salary_range,
                remote_type=remote_type,
                url=result.get("redirect_url", ""),
                posted_date=posted_date,
                description=description,
                requirements=[],  # Will be extracted by job analyzer tool
                nice_to_have=[],
                extracted_keywords=[],
                match_score=None  # Will be calculated by ranking function
            )

            return job

        except Exception as e:
            logger.error(f"Error parsing Adzuna job: {str(e)}")
            return None

    def rank_jobs(
        self,
        jobs: List[JobPosting],
        resume_data: Dict[str, Any]
    ) -> List[JobPosting]:
        """
        Rank jobs by match score based on resume data.

        Args:
            jobs: List of job postings
            resume_data: Parsed resume data dictionary

        Returns:
            Jobs sorted by match score (highest first)
        """
        resume_skills = set([skill.lower() for skill in resume_data.get("skills", [])])

        for job in jobs:
            # Simple keyword matching for now
            # TODO: Use LLM for more sophisticated matching
            job_text = f"{job.title} {job.description}".lower()

            # Count skill matches
            matching_skills = sum(1 for skill in resume_skills if skill in job_text)
            total_skills = len(resume_skills)

            # Calculate match score (0-100)
            if total_skills > 0:
                match_score = min(100, int((matching_skills / total_skills) * 100))
            else:
                match_score = 50  # Default if no skills

            # Bonus points for remote jobs if preferred
            if job.remote_type == RemoteType.REMOTE:
                match_score = min(100, match_score + 5)

            job.match_score = match_score

        # Sort by match score descending
        jobs.sort(key=lambda j: j.match_score or 0, reverse=True)

        return jobs

    def get_job_by_id(self, job_id: str, cached_jobs: List[JobPosting]) -> Optional[JobPosting]:
        """
        Get job details from cached results.

        Args:
            job_id: Job ID to retrieve
            cached_jobs: List of previously fetched jobs

        Returns:
            JobPosting if found, None otherwise
        """
        for job in cached_jobs:
            if job.id == job_id:
                return job
        return None


# Global service instance
job_search_service = JobSearchService()
