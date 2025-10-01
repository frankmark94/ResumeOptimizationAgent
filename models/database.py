"""SQLAlchemy database models and initialization."""
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from config import settings

Base = declarative_base()


class RemoteTypeDB(str, enum.Enum):
    """Job remote work type."""
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class ApplicationStatusDB(str, enum.Enum):
    """Application tracking status."""
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"


class Resume(Base):
    """Resume versions table."""
    __tablename__ = "resumes"

    id = Column(String, primary_key=True)
    version_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Contact info (flattened)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    location = Column(String)
    linkedin = Column(String)
    github = Column(String)

    # Content
    summary = Column(Text)
    skills = Column(Text)  # JSON string of list
    experience = Column(Text)  # JSON string of list
    education = Column(Text)  # JSON string of list
    certifications = Column(Text)  # JSON string of list

    raw_text = Column(Text)
    file_path = Column(String)

    # Relationships
    applications = relationship("Application", back_populates="resume")


class Job(Base):
    """Job postings table."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    salary_range = Column(String)
    remote_type = Column(SQLEnum(RemoteTypeDB), default=RemoteTypeDB.ONSITE)
    url = Column(String)
    posted_date = Column(DateTime)
    description = Column(Text, nullable=False)

    requirements = Column(Text)  # JSON string of list
    nice_to_have = Column(Text)  # JSON string of list
    extracted_keywords = Column(Text)  # JSON string of list

    match_score = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    applications = relationship("Application", back_populates="job")


class Application(Base):
    """Job applications tracking table."""
    __tablename__ = "applications"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    resume_version_id = Column(String, ForeignKey("resumes.id"), nullable=False)

    applied_date = Column(DateTime, default=datetime.now)
    status = Column(SQLEnum(ApplicationStatusDB), default=ApplicationStatusDB.APPLIED)
    notes = Column(Text)
    follow_up_date = Column(DateTime)
    cover_letter_path = Column(String)

    # Relationships
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")


class CoverLetterDB(Base):
    """Cover letters table."""
    __tablename__ = "cover_letters"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    file_path = Column(String)


# Database initialization
def init_db():
    """Initialize database and create all tables."""
    engine = create_engine(settings.database_url, echo=settings.debug)
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session."""
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    return Session()
