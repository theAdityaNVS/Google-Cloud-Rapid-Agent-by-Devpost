"""ErgoFlow AI — Telemetry Router"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models import BiometricTelemetry
from app.services import mongodb_service as db_svc

router = APIRouter()


@router.post("/biometrics", summary="Ingest biometric telemetry")
async def ingest_biometrics(
    data: BiometricTelemetry,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Ingest a single telemetry snapshot from wearable/desk sensor."""
    doc_id = await db_svc.insert_telemetry(db, data)
    return {"status": "ok", "inserted_id": doc_id}


@router.get("/latest", summary="Get latest telemetry for a user")
async def get_latest(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Fetch the most recent telemetry entry."""
    doc = await db_svc.get_latest_telemetry(db, user_id)
    if not doc:
        raise HTTPException(404, "No telemetry data found")
    return doc


@router.get("/history", summary="Get telemetry history")
async def get_history(
    user_id: str,
    days: int = 7,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Fetch telemetry entries from the last N days."""
    return await db_svc.get_telemetry_history(db, user_id, days)
