"""ErgoFlow AI — Agent Router"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.services import mongodb_service as db_svc
from app.services.agent_service import evaluate_user

router = APIRouter()


class EvaluateRequest(BaseModel):
    user_id: str


@router.post("/evaluate", summary="Trigger agent evaluation")
async def trigger_evaluation(
    req: EvaluateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Trigger the ErgoFlow agent evaluation loop.
    The agent will:
    1. Fetch latest biometric and feedback data
    2. Compute a fatigue score
    3. If score >= 6, generate and schedule a recovery routine
    4. Log all reasoning steps
    """
    result = await evaluate_user(db, req.user_id)
    return result


@router.get("/activity", summary="Get agent activity log")
async def get_activity(
    user_id: str,
    limit: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Fetch the agent's reasoning/activity log entries."""
    return await db_svc.get_activity_log(db, user_id, limit)
