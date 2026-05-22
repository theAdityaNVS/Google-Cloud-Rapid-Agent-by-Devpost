"""Pydantic V2 model for AgentActivityEntry."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class AgentActivityEntry(BaseModel):
    """
    A single entry in the agent's activity log.
    Stored in the `agent_activity` collection.
    """

    user_id: str = Field(..., description="Owner user ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    entry_type: Literal["analysis", "decision", "action", "tool_call", "result"] = Field(
        ..., description="Category of log entry"
    )
    message: str = Field(..., description="Human-readable description of what happened")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional structured details (fatigue_score, tool_name, etc.)"
    )

    model_config = {"populate_by_name": True, "json_encoders": {datetime: lambda v: v.isoformat()}}
