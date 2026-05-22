"""
ErgoFlow AI — Seed Data Script
Run: python -m app.utils.seed_data
Creates a default user profile and generates 7 days of demo data.
"""
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models import UserProfile, UserPreferences
from app.services import mongodb_service as db_svc
from app.services.simulator_service import generate_scenario


async def seed():
    """Drop existing data and seed fresh demo data."""
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]

    print("[db] Clearing existing data...")
    for col in ["user_profiles", "biometric_telemetry", "subjective_feedback",
                "orchestrated_routines", "agent_activity_log", "calendar_events"]:
        await db[col].delete_many({})

    print("[db] Creating indexes...")
    await db_svc.ensure_indexes(db)

    # Create default user
    user = UserProfile(
        user_id="usr_dev_9981",
        name="Aditya Nadamuni",
        preferences=UserPreferences(
            target_focus_session_limit_mins=90,
            preferred_routine_types=["lumbar_mobility", "shoulder_decompression", "eye_strain_relief"],
            suppress_during_meetings=True,
        ),
    )
    await db_svc.upsert_user(db, user)
    print(f"[user] User created: {user.name} ({user.user_id})")

    # Generate 7 days of mixed data (5 days moderate, 2 days high fatigue)
    print("[data] Generating 5 days of moderate data...")
    await generate_scenario(db, user.user_id, "moderate", days=5)

    print("[data] Generating 2 days of high fatigue data...")
    await generate_scenario(db, user.user_id, "high_fatigue", days=2)

    print("[seed] Seed data complete!")
    print(f"   Database: {settings.mongodb_db_name}")
    print(f"   User: {user.user_id}")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
