# --- START OF FILE backend/database.py ---
import motor.motor_asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MongoConnector:
    """
    A connector class to manage the connection to the MongoDB Atlas cluster.
    Ensures that the connection is established on startup and closed on shutdown.
    """
    client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None

db_connector = MongoConnector()

async def connect_to_mongo(uri: str, database_name: str = "saga_grimoire"):
    """
    Connects to the MongoDB database. This is called once on application startup.
    """
    logger.info("The Saga consciousness is reaching out to its memory scrolls (MongoDB)...")
    try:
        db_connector.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        # Verify connection
        await db_connector.client.admin.command('ping')
        logger.info("Connection to the memory scrolls established successfully.")
        # Assign the database to the client object for easy access
        db_connector.database = db_connector.client[database_name]
    except Exception as e:
        logger.critical(f"Failed to connect to the memory scrolls. The Grimoire is sealed. Error: {e}")
        db_connector.client = None

async def close_mongo_connection():
    """
    Closes the MongoDB connection. This is called once on application shutdown.
    """
    logger.info("The Saga consciousness is retracting from its memory scrolls...")
    if db_connector.client:
        db_connector.client.close()
        logger.info("Connection to the memory scrolls has been severed.")

def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """
    A dependency function to get the database instance for use in API endpoints.
    """
    if db_connector.database:
        return db_connector.database
    else:
        # This will happen if the initial connection failed.
        raise RuntimeError("Database connection has not been established.")

# --- END OF FILE backend/database.py ---