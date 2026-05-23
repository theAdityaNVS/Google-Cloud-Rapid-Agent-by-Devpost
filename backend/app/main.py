"""
ErgoFlow AI — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_to_mongo, close_mongo_connection, is_connected, get_database

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ergoflow")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    try:
        await connect_to_mongo()
        from app.services.mongodb_service import ensure_indexes
        await ensure_indexes(get_database())
    except Exception as e:
        logger.warning("MongoDB not available (%s). Endpoints requiring DB will return 503.", e)
    yield
    await close_mongo_connection()


app = FastAPI(
    title="ErgoFlow AI",
    description="Autonomous occupational health agent backend for software engineers",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ─────────────────────────────────────────────────────
from app.routers import telemetry, feedback, routines, agent, calendar, simulator, health  # noqa: E402

app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["Telemetry"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(routines.router, prefix="/api/agent/routines", tags=["Routines"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(simulator.router, prefix="/api/simulator", tags=["Simulator"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "service": "ErgoFlow AI",
        "version": "0.1.0",
        "mongodb_connected": is_connected(),
    }
