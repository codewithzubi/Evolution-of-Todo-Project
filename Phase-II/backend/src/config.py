# [Task]: T010, [From]: specs/001-task-crud-api/spec.md#Authentication
# [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
Application configuration using Pydantic Settings.

Loads environment variables from .env file. Never hardcodes secrets.
All configuration comes from environment variables or defaults.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    debug: bool = False
    environment: str = "development"
    log_level: str = "info"

    # Database
    database_url: str  # Must be set in .env

    # JWT Authentication
    jwt_secret: str  # Must be set in .env (from Better Auth)
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 168  # 7 days

    # Better Auth
    better_auth_secret: str  # Must be set in .env

    # API
    api_prefix: str = "/api"

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
