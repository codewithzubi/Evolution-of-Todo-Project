"""Application configuration."""
import os
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Authentication
    BETTER_AUTH_SECRET: str = os.getenv("BETTER_AUTH_SECRET", "")

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Phase-III: Groq API Configuration (switched from Cohere)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def __init__(self):
        """Validate required settings."""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")

        if not self.BETTER_AUTH_SECRET:
            raise ValueError("BETTER_AUTH_SECRET environment variable is required")

        if len(self.BETTER_AUTH_SECRET) < 32:
            raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters")

        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
