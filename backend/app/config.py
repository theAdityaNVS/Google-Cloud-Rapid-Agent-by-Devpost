"""
ErgoFlow AI — Application Configuration
Loads settings from environment variables / .env file via pydantic-settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central application settings sourced from environment variables."""

    # ── MongoDB ──────────────────────────────────────────────────────────
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI (Motor async driver)",
    )
    mongodb_db_name: str = Field(
        default="ergoflow_db",
        description="Name of the MongoDB database",
    )

    # ── Google Calendar OAuth (future) ───────────────────────────────────
    google_client_id: str = Field(default="", description="Google OAuth client ID")
    google_client_secret: str = Field(default="", description="Google OAuth client secret")
    google_redirect_uri: str = Field(
        default="http://localhost:8000/auth/callback",
        description="OAuth redirect URI",
    )

    # ── Agent Builder (future) ───────────────────────────────────────────
    agent_builder_endpoint: str = Field(default="", description="Vertex AI Agent Builder endpoint")
    agent_builder_api_key: str = Field(default="", description="Agent Builder API key")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton instance — import this everywhere
settings = Settings()
