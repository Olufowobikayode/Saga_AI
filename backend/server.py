--- START OF FILE backend/server.py ---
import os
import logging
from pathlib import Path
import uuid

from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional, List, Dict

# --- MongoDB Imports ---
from motor.motor_asyncio import AsyncIOMotorClient

# --- IMPORT THE MASTER ENGINE ---
from backend.engine import SagaEngine

logger = logging.getLogger(__name__)

# --- CONFIGURATION SETTINGS ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class Settings(BaseSettings):
    """The sacred scrolls that hold the secrets (environment variables) for the application."""
    gemini_api_key: str
    mongo_uri: str
    ip_geolocation_api_key: Optional[str] = Field(None, alias='IP_GEOLOCATION_API_KEY')

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- Pydantic Request/Response MODELS ---
class SagaRequest(BaseModel):
    """The format for a mortal's request for wisdom."""
    interest: Optional[str] = None
    product_name: Optional[str] = None
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None
    
    user_ip_address: Optional[str] = None
    target_country_name: Optional[str] = None
    product_category: Optional[str] = None
    product_subcategory: Optional[str] = None

    user_store_url: Optional[str] = None
    marketplace_link: Optional[str] = None
    product_selling_price: Optional[float] = None
    social_platforms_to_sell: Optional[List[str]] = None
    ads_daily_budget: Optional[float] = None
    number_of_days: Optional[int] = None
    amount_to_buy: Optional[int] = None

    buy_marketplace_link: Optional[str] = None
    sell_marketplace_link: Optional[str] = None

class SagaBlueprintRequest(BaseModel):
    """The format for requesting a detailed blueprint for a chosen vision."""
    session_id: str
    chosen_vision: Dict[str, Any]
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None

class SagaResponse(BaseModel):
    """The format for a prophecy sent back to the mortal realm."""
    prophecy_type: str
    data: Any

# --- FastAPI APP AND ROUTER ---
app = FastAPI(
    title="Saga AI",
    description="The digital throne of Saga, the Norse Goddess of Wisdom. This API is the gateway for solopreneurs to seek her prophetic counsel.",
    version="3.0.0" # Version bump to reflect major new feature
)

api_router = APIRouter(prefix="/api/v3")

db_client: AsyncIOMotorClient = None
database = None
engine: SagaEngine = None
app_settings: Settings = None

# --- API HEALTH CHECK ---
@api_router.get("/health", tags=["System"])
async def health_check():
    """A simple rite to confirm that the SagaEngine is awake and listening."""
    return {"message": "Saga is conscious and the Bifrost to this API is open."}

# --- PROPHECY ENDPOINTS ---

@api_router.post("/prophesy/new-ventures/visions", response_model=SagaResponse, tags=["New Ventures Prophecy"])
async def get_new_ventures_visions(request: SagaRequest):
    """
    PHASE 1: Seek a Prophecy of 10 initial business visions.
    Returns a session_id and a list of captivating ideas.
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    if not request.interest: raise HTTPException(status_code=400, detail="An 'interest' is required for this prophecy.")
    
    logger.info(f"A mortal seeks 10 visions for: {request.interest}")
    data = await engine.prophesy_initial_ventures(**request.model_dump())
    return SagaResponse(prophecy_type="new_venture_visions", data=data)

@api_router.post("/prophesy/new-ventures/blueprint", response_model=SagaResponse, tags=["New Ventures Prophecy"])
async def get_venture_blueprint(request: SagaBlueprintRequest):
    """
    PHASE 2: Seek a detailed Business Blueprint for a chosen vision.
    Requires the session_id from the visions phase and the chosen vision's object.
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    
    logger.info(f"A mortal seeks a blueprint for vision: {request.chosen_vision.get('title')}")
    try:
        data = await engine.prophesy_venture_blueprint(**request.model_dump())
        return SagaResponse(prophecy_type="venture_blueprint", data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"An unexpected error occurred while weaving the blueprint: {e}")
        raise HTTPException(status_code=500, detail="A disturbance occurred in the ether. The blueprint could not be completed.")

# ... (placeholder for other single-phase prophecy endpoints) ...

# --- Final App Configuration ---
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- The Awakening and Slumbering of the Engine ---
@app.on_event("startup")
async def startup_event():
    global db_client, database, engine, app_settings
    try:
        app_settings = Settings()
        logger.info("The sacred scrolls (settings) have been read.")
    except Exception as e:
        logger.critical(f"FATAL: The sacred scrolls are unreadable. Saga cannot awaken. Ensure .env is configured. Error: {e}")
        return
    if app_settings.mongo_uri:
        try:
            db_client = AsyncIOMotorClient(app_settings.mongo_uri)
            database = db_client.get_database("saga_ai_db")
            await database.command("ping")
            logger.info("A connection to the great database of histories, MongoDB, has been established.")
        except Exception as e:
            logger.error(f"Could not connect to the database of histories. Saga's memory will be fleeting. Error: {e}")
    if app_settings.gemini_api_key:
        engine = SagaEngine(gemini_api_key=app_settings.gemini_api_key, ip_geolocation_api_key=app_settings.ip_geolocation_api_key)

@app.on_event("shutdown")
async def shutdown_event():
    global db_client
    if db_client:
        db_client.close()
        logger.info("The connection to the database of histories has been closed. Saga slumbers.")
--- END OF FILE backend/server.py ---