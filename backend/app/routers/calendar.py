"""ErgoFlow AI — Calendar Router"""
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.services import calendar_service


router = APIRouter()


class CreateEventRequest(BaseModel):
    user_id: str
    title: str
    start_time: datetime
    duration_mins: int = 10
    description: str = ""


@router.get("/events", summary="List calendar events")
async def list_events(
    user_id: str,
    limit: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """List agent-scheduled calendar events for a user."""
    return await calendar_service.list_events(db, user_id, limit)


@router.post("/events", summary="Create calendar event")
async def create_event(
    req: CreateEventRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Create a new calendar event (mock implementation)."""
    event = await calendar_service.create_event(
        db, req.user_id, req.title, req.start_time,
        req.duration_mins, req.description,
    )
    return {"status": "ok", "event": event}
