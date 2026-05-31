from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client: AsyncIOMotorClient = None


async def connect_db():
    """Create MongoDB connection on app startup."""
    global client
    client = AsyncIOMotorClient(settings.mongo_uri)
    print(f"[DB] Connected to MongoDB at {settings.mongo_uri}")


async def close_db():
    """Close MongoDB connection on app shutdown."""
    global client
    if client:
        client.close()
        print("[DB] MongoDB connection closed")


def get_database():
    """Return the database instance."""
    return client[settings.mongo_db_name]


def get_collection(name: str):
    """Return a named collection."""
    return get_database()[name]
