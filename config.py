"""Configuration management for Job Optimization Agent."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    anthropic_api_key: str
    indeed_api_key: str | None = None
    linkedin_api_key: str | None = None
    adzuna_api_id: str | None = None
    adzuna_api_key: str | None = None

    # Database
    database_url: str = "sqlite:///./data/applications.db"

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"

    # File Paths
    base_dir: Path = Path(__file__).parent
    data_dir: Path = base_dir / "data"
    resume_dir: Path = data_dir / "resumes"
    generated_dir: Path = data_dir / "generated"

    # LLM Settings
    model_name: str = "claude-sonnet-4-20250514"
    temperature: float = 0.7
    max_tokens: int = 4096

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.resume_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        templates_dir = self.data_dir / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
