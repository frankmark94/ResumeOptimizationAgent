"""Resume parser tool for extracting structured data from resume files."""
import re
import json
from pathlib import Path
from typing import Dict, Any
import PyPDF2
import docx
from langchain.tools import tool
from models.schemas import ResumeData, ContactInfo, Experience, Education, Certification


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")
    return text


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        raise Exception(f"Error reading TXT: {str(e)}")
    return text


def extract_contact_info(text: str) -> ContactInfo:
    """Extract contact information using regex patterns."""
    # Email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else None

    # Phone
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0) if phone_match else None

    # LinkedIn
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    linkedin = linkedin_match.group(0) if linkedin_match else None

    # GitHub
    github_pattern = r'github\.com/[\w-]+'
    github_match = re.search(github_pattern, text, re.IGNORECASE)
    github = github_match.group(0) if github_match else None

    # Name (usually first line or two)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    name = lines[0] if lines else "Unknown"

    # Location (look for city, state pattern)
    location_pattern = r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2})'
    location_match = re.search(location_pattern, text)
    location = location_match.group(0) if location_match else None

    return ContactInfo(
        name=name,
        email=email,
        phone=phone,
        location=location,
        linkedin=linkedin,
        github=github
    )


def parse_resume_sections(text: str) -> Dict[str, Any]:
    """Parse resume into sections using common headers."""
    sections = {
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": []
    }

    # Common section headers
    summary_headers = ['summary', 'profile', 'objective', 'about']
    skills_headers = ['skills', 'technical skills', 'core competencies']
    experience_headers = ['experience', 'work experience', 'employment', 'professional experience']
    education_headers = ['education', 'academic background']
    cert_headers = ['certifications', 'certificates', 'licenses']

    # Split text into lines
    lines = text.split('\n')
    current_section = None
    section_content = []

    for line in lines:
        line_lower = line.lower().strip()

        # Check if line is a section header
        if any(header in line_lower for header in summary_headers):
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content)
            current_section = 'summary'
            section_content = []
        elif any(header in line_lower for header in skills_headers):
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content)
            current_section = 'skills'
            section_content = []
        elif any(header in line_lower for header in experience_headers):
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content)
            current_section = 'experience'
            section_content = []
        elif any(header in line_lower for header in education_headers):
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content)
            current_section = 'education'
            section_content = []
        elif any(header in line_lower for header in cert_headers):
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content)
            current_section = 'certifications'
            section_content = []
        elif current_section:
            section_content.append(line)

    # Add last section
    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content)

    return sections


def parse_skills(skills_text: str) -> list[str]:
    """Parse skills from text."""
    if not skills_text:
        return []

    # Split by common delimiters
    skills = re.split(r'[,;|\n•·]', skills_text)
    skills = [s.strip() for s in skills if s.strip() and len(s.strip()) > 1]

    return skills


@tool
def parse_resume(file_path: str = None) -> str:
    """Parse a resume file and extract structured information including contact info, summary, skills, experience, education, and certifications.

    Args:
        file_path: Absolute path to the resume file (PDF, DOCX, or TXT). If not provided, will check session state for uploaded file.

    Returns:
        JSON string with parsed resume data
    """
    from utils.session_state import get_session

    session = get_session()

    # Check if already parsed and cached
    if session.is_resume_parsed() and (not file_path or file_path == session.uploaded_resume_path):
        return json.dumps({
            "status": "cached",
            "message": "Resume already parsed in this session",
            **session.resume_parsed_data
        }, default=str)

    # If no file path provided, check session state
    if not file_path:
        if session.has_resume():
            file_path = session.uploaded_resume_path
        else:
            return json.dumps({
                "error": "No resume file found. Please upload a resume file first."
            })

    try:
        path = Path(file_path)

        if not path.exists():
            return json.dumps({"error": f"File not found: {file_path}"})

        # Extract text based on file type
        file_ext = path.suffix.lower()
        if file_ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            text = extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            text = extract_text_from_txt(file_path)
        else:
            return json.dumps({"error": f"Unsupported file type: {file_ext}"})

        if not text.strip():
            return json.dumps({"error": "No text could be extracted from the file"})

        # Extract contact info
        contact = extract_contact_info(text)

        # Parse sections
        sections = parse_resume_sections(text)

        # Parse skills
        skills = parse_skills(sections.get('skills', ''))

        # Create resume data object
        resume_data = ResumeData(
            contact=contact,
            summary=sections.get('summary', '').strip(),
            skills=skills,
            experience=[],  # TODO: Parse experience entries
            education=[],   # TODO: Parse education entries
            certifications=[],  # TODO: Parse certifications
            raw_text=text,
            file_path=file_path
        )

        # Cache parsed data in session
        parsed_dict = resume_data.model_dump()
        session.set_resume(file_path, parsed_dict)

        return json.dumps(parsed_dict, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": f"Failed to parse resume: {str(e)}"})
