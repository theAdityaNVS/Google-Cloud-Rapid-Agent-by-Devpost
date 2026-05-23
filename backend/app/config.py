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

    # ── MongoDB MCP Server ───────────────────────────────────────────────
    mcp_server_url: str = Field(
        default="",
        description="URL of the MongoDB MCP Server on Cloud Run (set after deployment)",
    )

    # ── Gemini API ───────────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="", description="Google AI Studio API key for Gemini")
    gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini model name")

    # ── Agent Builder (future) ───────────────────────────────────────────
    agent_builder_endpoint: str = Field(default="", description="Vertex AI Agent Builder endpoint")
    agent_builder_api_key: str = Field(default="", description="Agent Builder API key")
    google_cloud_project: str = Field(default="", description="Google Cloud Project ID")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton instance — import this everywhere
settings = Settings()
