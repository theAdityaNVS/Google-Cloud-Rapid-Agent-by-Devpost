"""
ErgoFlow AI — MongoDB CRUD Service Layer
Async CRUD operations for all collections using Motor.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models import (
    UserProfile, BiometricTelemetry, SubjectiveFeedback,
    OrchestratedRoutine, AgentActivityEntry,
)


# ── Collection Names ──────────────────────────────────────────────────────
USERS = "user_profiles"
TELEMETRY = "biometric_telemetry"
FEEDBACK = "subjective_feedback"
ROUTINES = "orchestrated_routines"
ACTIVITY = "agent_activity_log"
CALENDAR = "calendar_events"


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create indexes on first startup."""
    await db[TELEMETRY].create_index([("user_id", 1), ("timestamp", -1)])
    await db[FEEDBACK].create_index([("user_id", 1), ("timestamp", -1)])
    await db[ROUTINES].create_index([("user_id", 1), ("scheduled_timestamp", -1)])
    await db[ACTIVITY].create_index([("user_id", 1), ("created_at", -1)])


# ── Users ─────────────────────────────────────────────────────────────────
async def get_user(db: AsyncIOMotorDatabase, user_id: str) -> Optional[Dict]:
    return await db[USERS].find_one({"user_id": user_id}, {"_id": 0})


async def upsert_user(db: AsyncIOMotorDatabase, profile: UserProfile) -> None:
    await db[USERS].update_one(
        {"user_id": profile.user_id},
        {"$set": profile.model_dump()},
        upsert=True,
    )


# ── Telemetry ─────────────────────────────────────────────────────────────
async def insert_telemetry(db: AsyncIOMotorDatabase, data: BiometricTelemetry) -> str:
    result = await db[TELEMETRY].insert_one(data.model_dump())
    return str(result.inserted_id)


async def get_latest_telemetry(db: AsyncIOMotorDatabase, user_id: str) -> Optional[Dict]:
    return await db[TELEMETRY].find_one(
        {"user_id": user_id}, {"_id": 0}, sort=[("timestamp", -1)]
    )


async def get_telemetry_history(
    db: AsyncIOMotorDatabase, user_id: str, days: int = 7
) -> List[Dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    cursor = db[TELEMETRY].find(
        {"user_id": user_id, "timestamp": {"$gte": since}},
        {"_id": 0},
    ).sort("timestamp", 1)
    return await cursor.to_list(length=500)


# ── Feedback ──────────────────────────────────────────────────────────────
async def insert_feedback(db: AsyncIOMotorDatabase, data: SubjectiveFeedback) -> str:
    result = await db[FEEDBACK].insert_one(data.model_dump())
    return str(result.inserted_id)


async def get_feedback_history(
    db: AsyncIOMotorDatabase, user_id: str, limit: int = 20
) -> List[Dict]:
    cursor = db[FEEDBACK].find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_latest_feedback(db: AsyncIOMotorDatabase, user_id: str) -> Optional[Dict]:
    return await db[FEEDBACK].find_one(
        {"user_id": user_id}, {"_id": 0}, sort=[("timestamp", -1)]
    )


# ── Routines ──────────────────────────────────────────────────────────────
async def insert_routine(db: AsyncIOMotorDatabase, routine: OrchestratedRoutine) -> str:
    result = await db[ROUTINES].insert_one(routine.model_dump())
    return str(result.inserted_id)


async def get_next_routine(db: AsyncIOMotorDatabase, user_id: str) -> Optional[Dict]:
    return await db[ROUTINES].find_one(
        {"user_id": user_id, "status": "scheduled"},
        {"_id": 0},
        sort=[("scheduled_timestamp", 1)],
    )


async def get_routine_history(
    db: AsyncIOMotorDatabase, user_id: str, limit: int = 10
) -> List[Dict]:
    cursor = db[ROUTINES].find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("scheduled_timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def update_routine_status(
    db: AsyncIOMotorDatabase, user_id: str, scheduled_timestamp: datetime, status: str
) -> bool:
    result = await db[ROUTINES].update_one(
        {"user_id": user_id, "scheduled_timestamp": scheduled_timestamp},
        {"$set": {"status": status}},
    )
    return result.modified_count > 0


# ── Agent Activity Log ────────────────────────────────────────────────────
async def insert_activity(db: AsyncIOMotorDatabase, entry: AgentActivityEntry) -> str:
    result = await db[ACTIVITY].insert_one(entry.model_dump())
    return str(result.inserted_id)


async def insert_activities_bulk(
    db: AsyncIOMotorDatabase, entries: List[AgentActivityEntry]
) -> None:
    if entries:
        await db[ACTIVITY].insert_many([e.model_dump() for e in entries])


async def get_activity_log(
    db: AsyncIOMotorDatabase, user_id: str, limit: int = 30
) -> List[Dict]:
    cursor = db[ACTIVITY].find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


# ── Calendar Events ──────────────────────────────────────────────────────
async def insert_calendar_event(db: AsyncIOMotorDatabase, event: Dict) -> str:
    result = await db[CALENDAR].insert_one(event)
    return str(result.inserted_id)


async def get_calendar_events(
    db: AsyncIOMotorDatabase, user_id: str, limit: int = 10
) -> List[Dict]:
    cursor = db[CALENDAR].find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("start_time", -1).limit(limit)
    return await cursor.to_list(length=limit)
