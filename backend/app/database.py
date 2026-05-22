"""
ErgoFlow AI — Async MongoDB Client (Motor)
Manages the Motor client lifecycle and exposes a dependency for database access.
Falls back gracefully when MongoDB is unavailable.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger("ergoflow")

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None
_connected: bool = False


async def connect_to_mongo() -> None:
    """Create the Motor client and verify the connection."""
    global _client, _database, _connected
    _client = AsyncIOMotorClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000,  # 5s timeout, don't block forever
    )
    _database = _client[settings.mongodb_db_name]
    # Quick connectivity check
    await _client.admin.command("ping")
    _connected = True
    logger.info("Connected to MongoDB -- database: %s", settings.mongodb_db_name)


async def close_mongo_connection() -> None:
    """Gracefully close the Motor client."""
    global _client, _database, _connected
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        _connected = False
        logger.info("MongoDB connection closed")


def is_connected() -> bool:
    """Check if MongoDB is available."""
    return _connected


def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency that returns the current database handle."""
    if _database is None or not _connected:
        raise RuntimeError("Database not initialised -- MongoDB is not available")
    return _database
