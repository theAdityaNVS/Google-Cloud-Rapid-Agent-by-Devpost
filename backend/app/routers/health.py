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
    from app.config import settings
    if not settings.gemini_api_key:
        return {
            "service": "gemini_agent",
            "mode": "simulated",
            "status": "no_api_key",
            "ready": False,
        }
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        model.generate_content("ping")
        return {
            "service": "gemini_agent",
            "mode": "live",
            "model": settings.gemini_model,
            "status": "healthy",
            "ready": True,
        }
    except Exception as exc:
        return {
            "service": "gemini_agent",
            "mode": "live",
            "status": "error",
            "error": str(exc),
            "ready": False,
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
