"""Pydantic V2 models for UserProfile."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    """Ergonomic preferences for routine generation."""

    target_focus_session_limit_mins: int = Field(
        default=90, ge=15, le=180, description="Max focus-session length before a break is recommended"
    )
    preferred_routine_types: List[str] = Field(
        default_factory=lambda: ["lumbar_mobility", "shoulder_decompression", "eye_strain_relief"],
        description="Routine categories the user prefers",
    )
    suppress_during_meetings: bool = Field(
        default=True, description="Suppress break notifications during calendar meetings"
    )


class UserProfile(BaseModel):
    """Core user profile stored in the `users` collection."""

    user_id: str = Field(..., description="Unique user identifier, e.g. usr_dev_9981")
    name: str = Field(..., min_length=1, description="Display name")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    model_config = {"populate_by_name": True, "json_encoders": {datetime: lambda v: v.isoformat()}}
