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

    # Phase-II Integration (for MCP tools)
    phase2_api_url: str = "http://localhost:8000"  # Phase-II backend URL

    # OpenAI Configuration (Phase-III AI Chatbot)
    # [Task]: T316, [From]: specs/004-ai-chatbot/spec.md#FR-008
    openai_api_key: str = ""  # Required for AI agent; never hardcode
    openai_model: str = "gpt-4-turbo-preview"  # Model for multi-turn reasoning
    # [Task]: T321, [From]: specs/004-ai-chatbot/plan.md#Decision-4-Token-Window
    agent_max_messages: int = 20  # Context window: last 20 messages
    # [Task]: T320, [From]: specs/004-ai-chatbot/spec.md#CLARIFICATION-001
    agent_timeout: int = 30  # Timeout for agent execution (seconds)

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env (like NEXT_PUBLIC_*)


# Global settings instance
settings = Settings()
