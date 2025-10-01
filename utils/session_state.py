"""Session state management for maintaining context across agent interactions."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json


@dataclass
class SessionState:
    """Manages conversation context and uploaded file state."""

    # Resume state
    uploaded_resume_path: Optional[str] = None
    resume_parsed_data: Optional[Dict[str, Any]] = None
    resume_upload_time: Optional[datetime] = None

    # User profile
    user_profile: Dict[str, Any] = field(default_factory=dict)

    # Current job search context
    current_job_description: Optional[str] = None
    current_job_analysis: Optional[Dict[str, Any]] = None
    job_match_result: Optional[Dict[str, Any]] = None

    # Conversation history (lightweight - just key facts)
    conversation_summary: List[str] = field(default_factory=list)

    def has_resume(self) -> bool:
        """Check if a resume has been uploaded."""
        return self.uploaded_resume_path is not None

    def is_resume_parsed(self) -> bool:
        """Check if resume has been parsed."""
        return self.resume_parsed_data is not None

    def set_resume(self, file_path: str, parsed_data: Optional[Dict[str, Any]] = None):
        """Set resume upload information."""
        self.uploaded_resume_path = file_path
        self.resume_upload_time = datetime.now()
        if parsed_data:
            self.resume_parsed_data = parsed_data
        self.add_to_summary(f"Resume uploaded: {file_path}")

    def set_parsed_data(self, parsed_data: Dict[str, Any]):
        """Store parsed resume data."""
        self.resume_parsed_data = parsed_data
        self.add_to_summary("Resume parsed successfully")

    def set_job_description(self, description: str, analysis: Optional[Dict[str, Any]] = None):
        """Store current job search context."""
        self.current_job_description = description
        if analysis:
            self.current_job_analysis = analysis
        self.add_to_summary("Job description provided")

    def set_job_match(self, match_result: Dict[str, Any]):
        """Store job match analysis results."""
        self.job_match_result = match_result
        self.add_to_summary(f"Job match score: {match_result.get('match_score', 'N/A')}%")

    def add_to_summary(self, fact: str):
        """Add key fact to conversation summary."""
        self.conversation_summary.append(f"[{datetime.now().strftime('%H:%M')}] {fact}")
        # Keep only last 20 items
        if len(self.conversation_summary) > 20:
            self.conversation_summary = self.conversation_summary[-20:]

    def get_context_string(self) -> str:
        """Generate context string for agent."""
        context_parts = []

        if self.has_resume():
            context_parts.append(f"✓ Resume uploaded: {self.uploaded_resume_path}")
            if self.is_resume_parsed():
                name = self.resume_parsed_data.get('contact', {}).get('name', 'Unknown')
                context_parts.append(f"✓ Resume parsed for: {name}")
        else:
            context_parts.append("✗ No resume uploaded yet")

        if self.current_job_description:
            context_parts.append("✓ Job description provided")

        if self.job_match_result:
            score = self.job_match_result.get('match_score', 0)
            context_parts.append(f"✓ Job match analysis complete (Score: {score}%)")

        return " | ".join(context_parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Convert datetime to string
        if self.resume_upload_time:
            data['resume_upload_time'] = self.resume_upload_time.isoformat()
        return data

    def clear(self):
        """Clear all session data."""
        self.uploaded_resume_path = None
        self.resume_parsed_data = None
        self.resume_upload_time = None
        self.user_profile = {}
        self.current_job_description = None
        self.current_job_analysis = None
        self.job_match_result = None
        self.conversation_summary = []


# Global session state instance (for non-Streamlit usage)
_global_session = SessionState()


def get_session() -> SessionState:
    """Get the current session state."""
    try:
        import streamlit as st
        # Use Streamlit session state if available
        if 'app_session' not in st.session_state:
            st.session_state.app_session = SessionState()
        return st.session_state.app_session
    except (ImportError, RuntimeError):
        # Fall back to global session
        return _global_session


def reset_session():
    """Reset the session state."""
    session = get_session()
    session.clear()
