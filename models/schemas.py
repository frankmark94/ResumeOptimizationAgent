"""Pydantic schemas for data validation and serialization."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class RemoteType(str, Enum):
    """Job remote work type."""
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class ApplicationStatus(str, Enum):
    """Application tracking status."""
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"


# Resume Schemas
class ContactInfo(BaseModel):
    """Contact information from resume."""
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None


class Experience(BaseModel):
    """Work experience entry."""
    title: str
    company: str
    dates: str
    location: str | None = None
    bullets: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry."""
    degree: str
    institution: str
    dates: str
    gpa: str | None = None
    relevant_coursework: List[str] = Field(default_factory=list)


class Certification(BaseModel):
    """Professional certification."""
    name: str
    issuer: str
    date: str | None = None
    credential_id: str | None = None


class ResumeData(BaseModel):
    """Complete resume data structure."""
    id: str | None = None
    version_name: str = "Default"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    contact: ContactInfo
    summary: str | None = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)

    raw_text: str | None = None
    file_path: str | None = None


# Job Schemas
class JobPosting(BaseModel):
    """Job posting data structure."""
    id: str | None = None
    title: str
    company: str
    location: str
    salary_range: str | None = None
    remote_type: RemoteType = RemoteType.ONSITE
    url: str | None = None
    posted_date: datetime | None = None
    description: str

    requirements: List[str] = Field(default_factory=list)
    nice_to_have: List[str] = Field(default_factory=list)
    extracted_keywords: List[str] = Field(default_factory=list)

    match_score: float | None = None
    created_at: datetime = Field(default_factory=datetime.now)


# Application Tracking Schemas
class Application(BaseModel):
    """Job application tracking."""
    id: str | None = None
    job_id: str
    resume_version_id: str

    applied_date: datetime = Field(default_factory=datetime.now)
    status: ApplicationStatus = ApplicationStatus.APPLIED
    notes: str | None = None
    follow_up_date: datetime | None = None
    cover_letter_path: str | None = None

    # Denormalized fields for display
    job_title: str | None = None
    company_name: str | None = None


# Analysis Schemas
class SkillGap(BaseModel):
    """Skill gap analysis result."""
    missing_skills: List[str]
    matching_skills: List[str]
    partial_matches: List[str]
    gap_percentage: float


class ResumeOptimization(BaseModel):
    """Resume optimization suggestions."""
    section: str
    original_text: str
    optimized_text: str
    reasoning: str
    keywords_added: List[str] = Field(default_factory=list)


class JobMatchAnalysis(BaseModel):
    """Complete job match analysis."""
    job_id: str
    resume_id: str
    match_score: float
    skill_gap: SkillGap
    optimizations: List[ResumeOptimization]
    summary: str
    created_at: datetime = Field(default_factory=datetime.now)


# Cover Letter Schema
class CoverLetter(BaseModel):
    """Generated cover letter."""
    id: str | None = None
    job_id: str
    resume_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    file_path: str | None = None
