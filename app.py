"""
Streamlit UI for Job Research & Resume Optimization Agent
"""
import streamlit as st
import json
from pathlib import Path
import asyncio
from datetime import datetime

# Import agent and configuration
from agent.orchestrator import get_agent, reset_agent, arun_agent
from models.database import init_db
from config import settings

# Page configuration
st.set_page_config(
    page_title="Resume Optimization Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .tool-output {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'resume_uploaded' not in st.session_state:
        st.session_state.resume_uploaded = False
    if 'resume_path' not in st.session_state:
        st.session_state.resume_path = None


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file and return path."""
    save_dir = settings.resume_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(uploaded_file.name).suffix
    filename = f"resume_{timestamp}{file_extension}"
    file_path = save_dir / filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)


def display_chat_message(role: str, content: str):
    """Display a chat message with appropriate styling."""
    css_class = "user-message" if role == "user" else "assistant-message"
    icon = "👤" if role == "user" else "🤖"

    st.markdown(f"""
    <div class="chat-message {css_class}">
        <strong>{icon} {role.title()}</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    # Initialize
    initialize_session_state()
    init_db()  # Initialize database

    # Sidebar
    with st.sidebar:
        st.markdown("## 📄 Resume Optimization Agent")
        st.markdown("---")

        # Resume upload
        st.markdown("### Upload Your Resume")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format"
        )

        if uploaded_file is not None:
            # Save file
            file_path = save_uploaded_file(uploaded_file)
            st.session_state.resume_path = file_path
            st.session_state.resume_uploaded = True
            st.success(f"✅ Resume uploaded: {uploaded_file.name}")

            # Parse resume button
            if st.button("🔍 Parse Resume"):
                with st.spinner("Parsing resume..."):
                    agent = get_agent()
                    prompt = f"Please parse my resume at: {file_path}"
                    st.session_state.messages.append({"role": "user", "content": prompt})

        st.markdown("---")

        # Quick actions
        st.markdown("### Quick Actions")

        if st.button("🆕 New Conversation"):
            st.session_state.messages = []
            reset_agent()
            st.rerun()

        if st.button("💾 Save Session"):
            st.info("Session save feature coming soon!")

        st.markdown("---")

        # Info
        st.markdown("### About")
        st.markdown("""
        This AI agent helps you:
        - Parse and analyze resumes
        - Compare resumes to job postings
        - Identify skill gaps
        - Optimize resume content
        - Generate tailored bullets
        - Improve ATS compatibility
        """)

        # Settings
        st.markdown("---")
        st.markdown("### Settings")
        st.markdown(f"**Model:** {settings.model_name}")
        st.markdown(f"**Temperature:** {settings.temperature}")

    # Main content
    st.markdown('<div class="main-header">📄 Resume Optimization Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-powered career advisor to optimize your resume and find relevant jobs</div>', unsafe_allow_html=True)

    # Display welcome message if no messages
    if len(st.session_state.messages) == 0:
        st.info("""
        👋 **Welcome!** I'm your AI career advisor.

        **To get started:**
        1. Upload your resume using the sidebar
        2. Tell me about a job you're interested in
        3. I'll analyze the match and suggest optimizations

        **Example prompts:**
        - "Analyze my resume"
        - "I'm applying for a Senior Software Engineer role at Google. Here's the job description: [paste description]"
        - "Help me optimize my resume for this job"
        - "Generate better bullet points for my experience"
        """)

    # Chat history
    for message in st.session_state.messages:
        with st.container():
            display_chat_message(message["role"], message["content"])

    # Chat input
    user_input = st.chat_input("Ask me anything about your resume or job search...")

    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display user message
        with st.container():
            display_chat_message("user", user_input)

        # Get agent
        agent = get_agent()

        # Get response
        with st.spinner("Thinking..."):
            try:
                # Run agent asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(arun_agent(agent, user_input))

                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Display response
                with st.container():
                    display_chat_message("assistant", response)

                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please try again or rephrase your question.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Built with LangChain, Claude Sonnet 4, and Streamlit<br>
        💡 Tip: Be specific in your requests for better results
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
