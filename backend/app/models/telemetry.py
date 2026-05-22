"""Pydantic V2 models for BiometricTelemetry."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class TelemetryMetrics(BaseModel):
    """Biometric readings from wearable / desk sensors."""

    stand_hours_today: float = Field(..., ge=0, description="Cumulative stand hours so far today")
    active_calories_burned: int = Field(..., ge=0, description="Active calories burned today")
    steps_count_today: int = Field(..., ge=0, description="Total step count today")
    heart_rate_variability_hrv_ms: float = Field(
        ..., ge=0, description="Heart-rate variability in milliseconds"
    )


class TelemetryContext(BaseModel):
    """Environmental / calendar context at the time of the reading."""

    current_calendar_state: Literal["in_deep_focus_block", "in_meeting", "free"] = Field(
        ..., description="What the user is currently doing per their calendar"
    )
    consecutive_sitting_mins: int = Field(
        ..., ge=0, description="Minutes the user has been sitting continuously"
    )


class BiometricTelemetry(BaseModel):
    """Single telemetry snapshot stored in the `telemetry` collection."""

    user_id: str = Field(..., description="Owner user ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: TelemetryMetrics
    context: TelemetryContext

    model_config = {"populate_by_name": True, "json_encoders": {datetime: lambda v: v.isoformat()}}
