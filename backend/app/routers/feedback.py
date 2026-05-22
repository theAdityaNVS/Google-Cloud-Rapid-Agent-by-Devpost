"""ErgoFlow AI — Feedback Router"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models import SubjectiveFeedback
from app.services import mongodb_service as db_svc

router = APIRouter()


@router.post("/micro-prompt", summary="Submit micro-feedback")
async def submit_feedback(
    data: SubjectiveFeedback,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Receive 1-click physical degradation scores from the frontend."""
    doc_id = await db_svc.insert_feedback(db, data)
    return {"status": "ok", "inserted_id": doc_id}


@router.get("/history", summary="Get feedback history")
async def get_history(
    user_id: str,
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Fetch recent feedback entries."""
    return await db_svc.get_feedback_history(db, user_id, limit)


@router.get("/latest", summary="Get latest feedback")
async def get_latest(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Fetch the most recent feedback entry."""
    doc = await db_svc.get_latest_feedback(db, user_id)
    if not doc:
        raise HTTPException(404, "No feedback data found")
    return doc
