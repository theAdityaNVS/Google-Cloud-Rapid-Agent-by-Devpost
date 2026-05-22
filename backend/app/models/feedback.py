"""Pydantic V2 models for SubjectiveFeedback."""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class FeedbackAssessments(BaseModel):
    """Self-reported body-area scores (1 = fine → 5 = severe)."""

    lower_back_stiffness: int = Field(..., ge=1, le=5)
    shoulder_tension: int = Field(..., ge=1, le=5)
    neck_pain: int = Field(..., ge=1, le=5)
    eye_strain: int = Field(..., ge=1, le=5)
    mental_fatigue: int = Field(..., ge=1, le=5)


class SubjectiveFeedback(BaseModel):
    """A micro-prompt response stored in the `feedback` collection."""

    user_id: str = Field(..., description="Owner user ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assessments: FeedbackAssessments

    model_config = {"populate_by_name": True, "json_encoders": {datetime: lambda v: v.isoformat()}}
