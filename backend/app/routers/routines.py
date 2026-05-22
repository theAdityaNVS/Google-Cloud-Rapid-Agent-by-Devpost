"""ErgoFlow AI — Routines Router"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.services import mongodb_service as db_svc

router = APIRouter()


class StatusUpdate(BaseModel):
    status: str  # "in_progress", "completed", "dismissed"


@router.get("/next", summary="Get next scheduled routine")
async def get_next(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Fetch the next agent-orchestrated routine for the user."""
    routine = await db_svc.get_next_routine(db, user_id)
    if not routine:
        return {"message": "No routines scheduled", "routine": None}
    return routine


@router.get("/history", summary="Get routine history")
async def get_history(
    user_id: str,
    limit: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Fetch past orchestrated routines."""
    return await db_svc.get_routine_history(db, user_id, limit)
