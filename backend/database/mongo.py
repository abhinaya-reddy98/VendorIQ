from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from config import get_settings
from utils.logger import get_logger
from typing import Optional

logger = get_logger(__name__)
_async_client: Optional[AsyncIOMotorClient] = None


def get_async_client() -> AsyncIOMotorClient:
    global _async_client
    if _async_client is None:
        settings = get_settings()
        _async_client = AsyncIOMotorClient(settings.mongodb_uri)
        logger.info("MongoDB async client initialized")
    return _async_client


def get_db():
    settings = get_settings()
    client = get_async_client()
    return client[settings.mongodb_db_name]


async def close_db():
    global _async_client
    if _async_client:
        _async_client.close()
        _async_client = None
        logger.info("MongoDB connection closed")
