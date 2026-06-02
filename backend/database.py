from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client: AsyncIOMotorClient = None


async def connect_db():
    """Create MongoDB connection on app startup."""
    global client
    try:
        client = AsyncIOMotorClient(
            settings.mongo_uri,
            serverSelectionTimeoutMS=5000,
        )
        # Verify connection
        await client.admin.command("ping")
        print(f"[DB] Connected to MongoDB at {settings.mongo_uri}")
    except Exception as e:
        print(f"[DB] WARNING: Could not connect to MongoDB: {e}")
        print("[DB] App will start but database operations will fail.")


async def close_db():
    """Close MongoDB connection on app shutdown."""
    global client
    if client:
        client.close()
        print("[DB] MongoDB connection closed")


def get_database():
    """Return the database instance."""
    if client is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return client[settings.mongo_db_name]


def get_collection(name: str):
    """Return a named collection."""
    return get_database()[name]
