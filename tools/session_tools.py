"""Tools for checking and managing session state context."""
import json
from langchain.tools import tool
from utils.session_state import get_session


@tool
def check_resume_status() -> str:
    """Check if user has already uploaded a resume in this session.

    ALWAYS call this tool BEFORE asking the user to upload a resume or provide a file path.
    This prevents redundant requests and maintains conversation context.

    Returns:
        JSON string with resume status information
    """
    session = get_session()

    status = {
        "has_resume": session.has_resume(),
        "file_path": session.uploaded_resume_path,
        "is_parsed": session.is_resume_parsed(),
        "upload_time": session.resume_upload_time.isoformat() if session.resume_upload_time else None,
        "context": session.get_context_string()
    }

    if session.is_resume_parsed():
        # Include basic resume info if available
        contact = session.resume_parsed_data.get('contact', {})
        status["resume_info"] = {
            "name": contact.get('name'),
            "email": contact.get('email'),
            "skills_count": len(session.resume_parsed_data.get('skills', []))
        }

    return json.dumps(status, indent=2)


@tool
def get_session_context() -> str:
    """Get current session context including resume, job, and conversation state.

    Use this tool to understand what the user has already provided in the conversation.

    Returns:
        JSON string with session context
    """
    session = get_session()

    context = {
        "has_resume": session.has_resume(),
        "resume_path": session.uploaded_resume_path,
        "has_job_description": session.current_job_description is not None,
        "has_match_analysis": session.job_match_result is not None,
        "recent_activity": session.conversation_summary[-5:] if session.conversation_summary else []
    }

    return json.dumps(context, indent=2)
