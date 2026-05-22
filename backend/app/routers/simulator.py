"""ErgoFlow AI — Simulator Router"""
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.services.simulator_service import generate_scenario

router = APIRouter()


class SimulateRequest(BaseModel):
    user_id: str = Field(default="usr_dev_9981")
    scenario: Literal["high_fatigue", "moderate", "healthy"] = Field(default="high_fatigue")
    days: int = Field(default=7, ge=1, le=30)


@router.post("/generate", summary="Generate simulated data")
async def generate_data(
    req: SimulateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Generate realistic biometric and feedback data for demo purposes.
    Scenarios:
    - high_fatigue: Long sitting, few steps, high pain scores
    - moderate: Moderate activity, mixed pain levels
    - healthy: Regular breaks, high steps, low pain
    """
    result = await generate_scenario(db, req.user_id, req.scenario, req.days)
    return {"status": "ok", **result}
