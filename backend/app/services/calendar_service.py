"""
ErgoFlow AI — Calendar Service (Mock Implementation)
Stores calendar events in MongoDB. Ready to swap with real Google Calendar API.

To integrate real Google Calendar:
1. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
2. Implement OAuth2 flow in a separate auth router
3. Replace the mock methods below with google-api-python-client calls:
   - service = build('calendar', 'v3', credentials=creds)
   - service.events().insert(calendarId='primary', body=event).execute()
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services import mongodb_service as db_svc


async def list_events(
    db: AsyncIOMotorDatabase, user_id: str, limit: int = 10
) -> List[Dict]:
    """List upcoming agent-scheduled calendar events."""
    return await db_svc.get_calendar_events(db, user_id, limit)


async def create_event(
    db: AsyncIOMotorDatabase,
    user_id: str,
    title: str,
    start_time: datetime,
    duration_mins: int = 10,
    description: str = "",
) -> Dict:
    """Create a new calendar event (mock: stored in MongoDB)."""
    event = {
        "user_id": user_id,
        "event_id": f"cal_evt_{int(start_time.timestamp())}",
        "title": title,
        "start_time": start_time,
        "end_time": start_time + timedelta(minutes=duration_mins),
        "description": description,
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc),
    }
    await db_svc.insert_calendar_event(db, event)
    return event


async def delete_event(
    db: AsyncIOMotorDatabase, user_id: str, event_id: str
) -> bool:
    """Delete a calendar event by ID (mock)."""
    result = await db.calendar_events.delete_one(
        {"user_id": user_id, "event_id": event_id}
    )
    return result.deleted_count > 0
