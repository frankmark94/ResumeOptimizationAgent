"""
Document Generation Tools - Agent tools for creating resumes and cover letters
"""
import json
import logging
from langchain.tools import tool
from typing import Optional
from services.document_service import document_service
from services.job_search_service import job_search_service
from utils.session_state import get_session
from langchain_anthropic import ChatAnthropic
from config import settings

logger = logging.getLogger(__name__)


@tool
def generate_optimized_resume(
    job_id: str,
    file_format: str = 'pdf'
) -> str:
    """
    Generate an optimized resume PDF/DOCX for a specific job posting.

    This tool creates a tailored resume that highlights relevant skills and experience
    for the target job. It uses the parsed resume data and optimizes content based on
    job requirements.

    PREREQUISITES:
    - Requires a valid job_id from search results
    - If user doesn't specify which job, use list_available_jobs() FIRST
    - If no jobs in session, ask user to search for jobs or provide criteria
    - NEVER call this tool without a specific job_id

    Use this tool ONLY when you have a confirmed job_id from the user or session.

    Args:
        job_id: Job ID from search results (REQUIRED - get from list_available_jobs())
        file_format: Output format - 'pdf' or 'docx' (default: 'pdf')

    Returns:
        JSON string with file path and document metadata

    Example:
        generate_optimized_resume("12345", "pdf")
    """
    try:
        session = get_session()

        # Get resume data
        if not session.is_resume_parsed():
            return json.dumps({
                "status": "error",
                "message": "No resume found. Please upload and parse a resume first."
            })

        resume_data = session.resume_parsed_data

        # Get job posting
        cached_jobs = session.current_job_search_results or []
        job = job_search_service.get_job_by_id(job_id, cached_jobs)

        if not job:
            return json.dumps({
                "status": "error",
                "message": f"Job ID {job_id} not found in current search results"
            })

        # TODO: Use LLM to optimize specific sections based on job requirements
        # For now, use basic resume data
        optimizations = {}

        # Generate summary optimization using LLM
        try:
            llm = ChatAnthropic(
                model=settings.model_name,
                temperature=0.7,
                api_key=settings.anthropic_api_key
            )

            current_summary = resume_data.get('summary', '')
            skills = ", ".join(resume_data.get('skills', [])[:10])

            prompt = f"""Rewrite this professional summary to better match the job requirements.

Current Summary:
{current_summary}

Target Job:
Title: {job.title}
Company: {job.company}
Key Requirements: {job.description[:500]}

Candidate Skills: {skills}

Create a 2-3 sentence professional summary that:
1. Highlights relevant experience for this role
2. Incorporates keywords from the job description
3. Emphasizes quantifiable achievements
4. Is ATS-friendly and professional

Return only the rewritten summary, no explanations."""

            response = llm.invoke(prompt)
            optimizations['summary'] = response.content

        except Exception as e:
            logger.warning(f"Could not optimize summary: {str(e)}")

        # Generate document
        if file_format.lower() == 'docx':
            file_bytes = document_service.generate_resume_docx(
                resume_data, job, optimizations
            )
        else:
            file_bytes = document_service.generate_resume_pdf(
                resume_data, job, optimizations
            )

        # Save to disk
        file_path = document_service.save_document(
            file_bytes, job_id, 'resume', file_format
        )

        # Store in session
        session.generated_documents[f"resume_{job_id}"] = file_path
        session.add_to_summary(f"Generated resume for {job.title} at {job.company}")

        result = {
            "status": "success",
            "document_type": "resume",
            "file_format": file_format,
            "file_path": file_path,
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company
            },
            "message": f"Resume generated successfully for {job.title} at {job.company}"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Error generating resume: {str(e)}"
        })


@tool
def generate_cover_letter(
    job_id: str,
    tone: str = 'professional'
) -> str:
    """
    Generate a personalized cover letter PDF for a specific job posting.

    This tool creates a compelling cover letter that connects the candidate's experience
    to the job requirements. The content is generated by an LLM and formatted professionally.

    Use this tool when the user asks to create or generate a cover letter.

    Args:
        job_id: Job ID from search results
        tone: Writing tone - 'professional', 'enthusiastic', or 'conversational' (default: 'professional')

    Returns:
        JSON string with file path and document metadata

    Example:
        generate_cover_letter("12345", "professional")
    """
    try:
        session = get_session()

        # Get resume data
        if not session.is_resume_parsed():
            return json.dumps({
                "status": "error",
                "message": "No resume found. Please upload and parse a resume first."
            })

        resume_data = session.resume_parsed_data

        # Get job posting
        cached_jobs = session.current_job_search_results or []
        job = job_search_service.get_job_by_id(job_id, cached_jobs)

        if not job:
            return json.dumps({
                "status": "error",
                "message": f"Job ID {job_id} not found in current search results"
            })

        # Generate cover letter content using LLM
        try:
            llm = ChatAnthropic(
                model=settings.model_name,
                temperature=0.7,
                api_key=settings.anthropic_api_key
            )

            name = resume_data.get('contact', {}).get('name', 'the candidate')
            experience_summary = "\n".join([
                f"- {exp.get('title')} at {exp.get('company')}"
                for exp in resume_data.get('experience', [])[:3]
            ])
            skills = ", ".join(resume_data.get('skills', [])[:15])

            tone_instructions = {
                'professional': 'formal and professional',
                'enthusiastic': 'enthusiastic and energetic while remaining professional',
                'conversational': 'conversational yet professional, showing personality'
            }

            tone_style = tone_instructions.get(tone, 'professional')

            prompt = f"""Write a compelling cover letter for this job application.

Candidate: {name}
Recent Experience:
{experience_summary}

Key Skills: {skills}

Target Job:
Title: {job.title}
Company: {job.company}
Description: {job.description[:1000]}

Write a {tone_style} cover letter that:
1. Opens with a strong hook showing enthusiasm for the role
2. Connects 2-3 specific experiences/achievements to job requirements
3. Demonstrates knowledge of the company
4. Shows genuine interest and cultural fit
5. Closes with a clear call to action

Structure: 3-4 paragraphs, 250-350 words total.
Format: Plain text paragraphs separated by blank lines.
Do NOT include contact info, date, or signature (those will be added automatically).
Return only the cover letter body."""

            response = llm.invoke(prompt)
            cover_letter_content = response.content

        except Exception as e:
            logger.error(f"Error generating cover letter content: {str(e)}")
            return json.dumps({
                "status": "error",
                "message": f"Error generating cover letter content: {str(e)}"
            })

        # Generate PDF
        file_bytes = document_service.generate_cover_letter_pdf(
            resume_data, job, cover_letter_content
        )

        # Save to disk
        file_path = document_service.save_document(
            file_bytes, job_id, 'cover_letter', 'pdf'
        )

        # Store in session
        session.generated_documents[f"cover_letter_{job_id}"] = file_path
        session.add_to_summary(f"Generated cover letter for {job.title} at {job.company}")

        result = {
            "status": "success",
            "document_type": "cover_letter",
            "file_format": "pdf",
            "file_path": file_path,
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company
            },
            "message": f"Cover letter generated successfully for {job.title} at {job.company}"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Error generating cover letter: {str(e)}"
        })


@tool
def list_generated_documents() -> str:
    """
    List all documents generated in the current session.

    Use this tool when the user wants to see what documents they've created.

    Returns:
        JSON string with list of generated documents

    Example:
        list_generated_documents()
    """
    try:
        session = get_session()
        documents = session.generated_documents

        if not documents:
            return json.dumps({
                "status": "no_documents",
                "message": "No documents have been generated in this session.",
                "count": 0
            })

        result = {
            "status": "success",
            "count": len(documents),
            "documents": [
                {
                    "key": key,
                    "file_path": path,
                    "document_type": "resume" if "resume" in key else "cover_letter"
                }
                for key, path in documents.items()
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Error listing documents: {str(e)}"
        })
