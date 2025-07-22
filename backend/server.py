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

# --- IMPORT THE MASTER ENGINE AND NEW DISCOVERY TOOL ---
from backend.engine import SagaEngine
from backend.marketplace_finder import find_legit_marketplaces

logger = logging.getLogger(__name__)

# --- CONFIGURATION SETTINGS (Unchanged) ---
class Settings(BaseSettings):
    gemini_api_key: str
    mongo_uri: str
    ip_geolocation_api_key: Optional[str] = Field(None, alias='IP_GEOLOCATION_API_KEY')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- Pydantic Models (Unchanged) ---
class SagaRequest(BaseModel):
    interest: str
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None
    user_ip_address: Optional[str] = None
    target_country_name: Optional[str] = None

class ContentSparksRequest(BaseModel):
    strategy_session_id: str
    tactical_interest: str
    link: Optional[str] = None
    link_description: Optional[str] = None

# ... (and other specific request models)

class SagaResponse(BaseModel):
    prophecy_type: str
    data: Any

# --- FastAPI APP AND ROUTER ---
app = FastAPI(
    title="Saga AI",
    description="The digital throne of Saga, the Norse Goddess of Wisdom.",
    version="5.1.0" # Version bump for new discovery feature
)
api_router = APIRouter(prefix="/api/v5")
engine: SagaEngine = None

# --- API HEALTH CHECK ---
@api_router.get("/health", tags=["System & Discovery"])
async def health_check():
    return {"message": "Saga is conscious and the Bifrost to this API is open."}

# --- NEW Marketplace Discovery Endpoint ---
@api_router.post("/discover-new-marketplaces", tags=["System & Discovery"])
async def discover_marketplaces_endpoint():
    """
    Commands Saga's scout to search the web for new e-commerce marketplaces.
    This is a long-running task that will update the server's knowledge base.
    """
    logger.info("A command has been issued to discover new realms of commerce.")
    try:
        # NOTE: For a production app, this synchronous, long-running task should be
        # moved to a background worker (e.g., using FastAPI's BackgroundTasks or Celery)
        # to avoid blocking the server.
        results = find_legit_marketplaces()
        return {"status": "Discovery complete", "found_domains": results}
    except Exception as e:
        logger.error(f"The marketplace discovery mission failed: {e}")
        raise HTTPException(status_code=500, detail="The discovery mission failed. Check server logs for details.")


# --- PROPHECY ENDPOINTS (Unchanged) ---

@api_router.post("/prophesy/grand-strategy", response_model=SagaResponse, tags=["1. Grand Strategy (Start Here)"])
async def get_grand_strategy(request: SagaRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_grand_strategy(**request.model_dump())
    return SagaResponse(prophecy_type="grand_strategy", data=data)

@api_router.post("/prophesy/content-saga/sparks", response_model=SagaResponse, tags=["2. Tactical Prophecies (Content)"])
async def get_content_sparks(request: ContentSparksRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_content_sparks(**request.model_dump())
        return SagaResponse(prophecy_type="content_sparks", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

# ... (All other prophecy endpoints remain unchanged) ...


# --- Final App Configuration & Startup/Shutdown (Unchanged) ---
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global engine
    settings = Settings()
    if settings.gemini_api_key:
        engine = SagaEngine(gemini_api_key=settings.gemini_api_key, ip_geolocation_api_key=settings.ip_geolocation_api_key)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Saga slumbers.")
--- END OF FILE backend/server.py ---