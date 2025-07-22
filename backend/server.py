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
    """The general format for a mortal's request for wisdom."""
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
    """The format for requesting a detailed blueprint for a chosen new venture vision."""
    session_id: str
    chosen_vision: Dict[str, Any]
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None

# --- NEW Request Models for the Content Saga Workflow ---
class ContentSparksRequest(BaseModel):
    interest: str
    link: Optional[str] = None
    link_description: Optional[str] = None

class SocialPostRequest(BaseModel):
    session_id: str
    spark_id: str
    platform: str
    length: str
    post_type: str
    link: Optional[str] = None
    link_description: Optional[str] = None

class CommentRequest(BaseModel):
    session_id: str
    spark_id: str
    post_to_comment_on: str # This is mandatory as per our correction
    link: Optional[str] = None
    link_description: Optional[str] = None

class BlogPostRequest(BaseModel):
    session_id: str
    spark_id: str
    link: Optional[str] = None
    link_description: Optional[str] = None

class SagaResponse(BaseModel):
    """The format for a prophecy sent back to the mortal realm."""
    prophecy_type: str
    data: Any

# --- FastAPI APP AND ROUTER ---
app = FastAPI(
    title="Saga AI",
    description="The digital throne of Saga, the Norse Goddess of Wisdom.",
    version="4.0.0"
)
api_router = APIRouter(prefix="/api/v4")
engine: SagaEngine = None

# --- API HEALTH CHECK ---
@api_router.get("/health", tags=["System"])
async def health_check():
    return {"message": "Saga is conscious and the Bifrost to this API is open."}

# --- New Ventures Prophecy Endpoints (These are complete and functional) ---
@api_router.post("/prophesy/new-ventures/visions", response_model=SagaResponse, tags=["New Ventures Prophecy"])
async def get_new_ventures_visions(request: SagaRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    if not request.interest: raise HTTPException(status_code=400, detail="An 'interest' is required for this prophecy.")
    data = await engine.prophesy_initial_ventures(**request.model_dump())
    return SagaResponse(prophecy_type="new_venture_visions", data=data)

@api_router.post("/prophesy/new-ventures/blueprint", response_model=SagaResponse, tags=["New Ventures Prophecy"])
async def get_venture_blueprint(request: SagaBlueprintRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_venture_blueprint(**request.model_dump())
        return SagaResponse(prophecy_type="venture_blueprint", data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- NEW Content Saga Prophecy Endpoints ---

@api_router.post("/prophesy/content-saga/sparks", response_model=SagaResponse, tags=["Content Saga Prophecy"])
async def get_content_sparks(request: ContentSparksRequest):
    """PHASE 1: Seek 5 initial 'Content Sparks' for a given interest."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_content_sparks(**request.model_dump())
    return SagaResponse(prophecy_type="content_sparks", data=data)

@api_router.post("/prophesy/content-saga/social-post", response_model=SagaResponse, tags=["Content Saga Prophecy"])
async def get_social_post(request: SocialPostRequest):
    """PHASE 2a: Generate a platform-specific social media post from a spark."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_social_media_post(**request.model_dump())
        return SagaResponse(prophecy_type="social_post", data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.post("/prophesy/content-saga/comment", response_model=SagaResponse, tags=["Content Saga Prophecy"])
async def get_insightful_comment(request: CommentRequest):
    """PHASE 2b: Generate an insightful comment from a spark."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_insightful_comment(**request.model_dump())
        return SagaResponse(prophecy_type="insightful_comment", data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.post("/prophesy/content-saga/blog-post", response_model=SagaResponse, tags=["Content Saga Prophecy"])
async def get_blog_post(request: BlogPostRequest):
    """PHASE 2c: Generate a full blog post from a spark."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_blog_post_from_spark(**request.model_dump())
        return SagaResponse(prophecy_type="blog_post", data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Final App Configuration & Startup/Shutdown ---
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
    global engine, app_settings
    try:
        app_settings = Settings()
        logger.info("The sacred scrolls (settings) have been read.")
    except Exception as e:
        logger.critical(f"FATAL: The sacred scrolls are unreadable. Saga cannot awaken. Ensure .env is configured. Error: {e}")
        return
    
    # MongoDB connection logic would go here
    
    if app_settings.gemini_api_key:
        engine = SagaEngine(gemini_api_key=app_settings.gemini_api_key, ip_geolocation_api_key=app_settings.ip_geolocation_api_key)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Saga slumbers.")
--- END OF FILE backend/server.py ---