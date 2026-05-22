import os
import time
from fastapi import APIRouter
from app.database import is_connected

router = APIRouter()
START_TIME = time.time()

@router.get("/ping")
async def ping():
    return {
        "status": "ok",
        "message": "pong",
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }

@router.get("/db")
async def db_status():
    connected = is_connected()
    return {
        "service": "mongodb_atlas",
        "status": "connected" if connected else "disconnected",
        "ready": connected
    }

@router.get("/gemini")
async def gemini_status():
    # Placeholder for future Google Cloud Vertex AI / Gemini integration
    has_key = "GEMINI_API_KEY" in os.environ or "GOOGLE_APPLICATION_CREDENTIALS" in os.environ
    return {
        "service": "gemini_agent",
        "mode": "live" if has_key else "simulated",
        "status": "configured" if has_key else "using_mock_fallback",
        "ready": True
    }

@router.get("/status")
async def full_system_status():
    connected = is_connected()
    return {
        "status": "healthy" if connected else "degraded",
        "dependencies": {
            "database": "up" if connected else "down",
            "llm_engine": "simulated"
        },
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }
