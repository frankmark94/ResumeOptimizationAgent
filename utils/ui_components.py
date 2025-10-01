"""
UI Components - Reusable Streamlit components for rich content rendering
"""
import streamlit as st
from typing import List, Dict, Any, Optional
from models.schemas import JobPosting
from pathlib import Path


def render_job_card(job: JobPosting, index: int):
    """
    Render a job posting as an expandable card with match score and action buttons.

    Args:
        job: JobPosting object
        index: Index for unique widget keys
    """
    # Match score color
    match_score = job.match_score or 0
    if match_score >= 80:
        score_color = "🟢"
    elif match_score >= 60:
        score_color = "🟡"
    else:
        score_color = "🔴"

    # Card header
    with st.expander(f"{score_color} **{job.title}** at **{job.company}** - {match_score}% match", expanded=index==0):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**📍 Location:** {job.location}")
            if job.salary_range:
                st.markdown(f"**💰 Salary:** {job.salary_range}")
            st.markdown(f"**🏠 Remote Type:** {job.remote_type.value.title()}")
            if job.posted_date:
                st.markdown(f"**📅 Posted:** {job.posted_date.strftime('%B %d, %Y')}")
            if job.url:
                st.markdown(f"[🔗 View Original Posting]({job.url})")

        with col2:
            st.metric("Match Score", f"{match_score}%")

        st.markdown("---")
        st.markdown("**Description:**")

        # Show preview or full description
        desc_preview = job.description[:500] + "..." if len(job.description) > 500 else job.description
        st.markdown(desc_preview)

        if len(job.description) > 500:
            if st.button("Show Full Description", key=f"desc_{job.id}_{index}"):
                st.markdown(job.description)

        st.markdown("---")

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Generate Resume", key=f"resume_{job.id}_{index}", use_container_width=True):
                # Trigger resume generation via agent
                prompt = f"Generate an optimized resume for job ID: {job.id}"
                st.session_state.pending_action = prompt
                st.rerun()

        with col2:
            if st.button("✉️ Generate Cover Letter", key=f"cover_{job.id}_{index}", use_container_width=True):
                # Trigger cover letter generation via agent
                prompt = f"Generate a cover letter for job ID: {job.id}"
                st.session_state.pending_action = prompt
                st.rerun()

        with col3:
            if st.button("📊 Analyze Match", key=f"analyze_{job.id}_{index}", use_container_width=True):
                # Trigger job analysis via agent
                prompt = f"Analyze my match for job ID: {job.id} and tell me what gaps I need to address"
                st.session_state.pending_action = prompt
                st.rerun()


def render_job_search_results(jobs: List[JobPosting]):
    """
    Render multiple job cards from search results.

    Args:
        jobs: List of JobPosting objects
    """
    if not jobs:
        st.info("No job results to display. Try searching for jobs!")
        return

    st.markdown(f"### 🎯 Found {len(jobs)} Jobs")
    st.markdown("---")

    for i, job in enumerate(jobs):
        render_job_card(job, i)


def render_document_download(file_path: str, doc_type: str = "Document"):
    """
    Render a download button for a generated document.

    Args:
        file_path: Path to the document file
        doc_type: Type of document (e.g., "Resume", "Cover Letter")
    """
    try:
        path = Path(file_path)

        if not path.exists():
            st.error(f"File not found: {file_path}")
            return

        # Determine MIME type
        suffix = path.suffix.lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain'
        }
        mime_type = mime_types.get(suffix, 'application/octet-stream')

        # Read file
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        # Create download button
        filename = path.name
        st.download_button(
            label=f"⬇️ Download {doc_type} ({suffix.upper()})",
            data=file_bytes,
            file_name=filename,
            mime=mime_type,
            key=f"download_{filename}",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Error preparing download: {str(e)}")


def render_document_card(file_path: str, job_title: str, company: str, doc_type: str):
    """
    Render a card showing generated document info with download button.

    Args:
        file_path: Path to the document
        job_title: Job title the document was created for
        company: Company name
        doc_type: "Resume" or "Cover Letter"
    """
    icon = "📄" if doc_type == "Resume" else "✉️"

    with st.container():
        st.markdown(f"""
        <div style="
            border: 2px solid #1f77b4;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background-color: #f0f8ff;
        ">
            <h4>{icon} {doc_type} Generated!</h4>
            <p><strong>Position:</strong> {job_title}</p>
            <p><strong>Company:</strong> {company}</p>
        </div>
        """, unsafe_allow_html=True)

        render_document_download(file_path, doc_type)


def parse_agent_response_for_ui(response: str, session) -> Dict[str, Any]:
    """
    Parse agent response to detect if job search results or documents were generated.

    Args:
        response: Agent's text response
        session: Current session state

    Returns:
        Dictionary with:
            - has_jobs: bool
            - jobs: List[JobPosting]
            - has_documents: bool
            - documents: List[Dict]
    """
    result = {
        "has_jobs": False,
        "jobs": [],
        "has_documents": False,
        "documents": []
    }

    # Check for job search results in session
    if session.current_job_search_results:
        result["has_jobs"] = True
        result["jobs"] = session.current_job_search_results

    # Check for newly generated documents
    if session.generated_documents:
        # Get last document (newly generated)
        for key, file_path in list(session.generated_documents.items())[-3:]:  # Last 3
            doc_type = "Resume" if "resume" in key else "Cover Letter"
            result["documents"].append({
                "file_path": file_path,
                "doc_type": doc_type
            })

        if result["documents"]:
            result["has_documents"] = True

    return result
