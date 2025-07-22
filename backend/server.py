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

# --- CONFIGURATION SETTINGS (Unchanged) ---
class Settings(BaseSettings):
    gemini_api_key: str
    mongo_uri: str
    ip_geolocation_api_key: Optional[str] = Field(None, alias='IP_GEOLOCATION_API_KEY')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- Pydantic Models (Updated for new workflow) ---
class SagaRequest(BaseModel):
    """General request, now primarily for the Grand Strategy."""
    interest: str
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None
    user_ip_address: Optional[str] = None
    target_country_name: Optional[str] = None

# --- NEW Request Models for the Strategy-First Workflow ---
class ContentSparksRequest(BaseModel):
    strategy_session_id: str
    tactical_interest: str # This comes from a content pillar
    link: Optional[str] = None
    link_description: Optional[str] = None

class SocialPostRequest(BaseModel):
    strategy_session_id: str
    spark_id: str
    platform: str
    length: str
    post_type: str
    link: Optional[str] = None
    link_description: Optional[str] = None

class CommentRequest(BaseModel):
    strategy_session_id: str
    spark_id: str
    post_to_comment_on: str
    link: Optional[str] = None
    link_description: Optional[str] = None

class BlogPostRequest(BaseModel):
    strategy_session_id: str
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
    version="5.0.0" # Version bump for major architectural change
)
api_router = APIRouter(prefix="/api/v5")
engine: SagaEngine = None

@api_router.get("/health", tags=["System"])
async def health_check():
    return {"message": "Saga is conscious and the Bifrost to this API is open."}

# --- PROPHECY ENDPOINTS ---

@api_router.post("/prophesy/grand-strategy", response_model=SagaResponse, tags=["1. Grand Strategy (Start Here)"])
async def get_grand_strategy(request: SagaRequest):
    """
    FORGE a Grand Strategy. This is the mandatory first step.
    Returns a master plan and the `strategy_session_id` required for all other prophecies.
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_grand_strategy(**request.model_dump())
    return SagaResponse(prophecy_type="grand_strategy", data=data)

@api_router.post("/prophesy/content-saga/sparks", response_model=SagaResponse, tags=["2. Tactical Prophecies (Content)"])
async def get_content_sparks(request: ContentSparksRequest):
    """
    GET Content Sparks for a tactical interest derived from a Content Pillar.
    Requires a valid `strategy_session_id`.
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_content_sparks(**request.model_dump())
        return SagaResponse(prophecy_type="content_sparks", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

@api_router.post("/prophesy/content-saga/social-post", response_model=SagaResponse, tags=["2. Tactical Prophecies (Content)"])
async def get_social_post(request: SocialPostRequest):
    """Generate a platform-specific social media post. Requires a `strategy_session_id`."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_social_media_post(**request.model_dump())
        return SagaResponse(prophecy_type="social_post", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

@api_router.post("/prophesy/content-saga/comment", response_model=SagaResponse, tags=["2. Tactical Prophecies (Content)"])
async def get_insightful_comment(request: CommentRequest):
    """Generate an insightful comment. Requires a `strategy_session_id`."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_insightful_comment(**request.model_dump())
        return SagaResponse(prophecy_type="insightful_comment", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

@api_router.post("/prophesy/content-saga/blog-post", response_model=SagaResponse, tags=["2. Tactical Prophecies (Content)"])
async def get_blog_post(request: BlogPostRequest):
    """Generate a full blog post. Requires a `strategy_session_id`."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_blog_post_from_spark(**request.model_dump())
        return SagaResponse(prophecy_type="blog_post", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

# ... (Other endpoints for Commerce, Arbitrage etc. would also be refactored here to require the strategy_session_id) ...

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
    global engine
    # ... (code is complete and unchanged) ...
    settings = Settings()
    if settings.gemini_api_key:
        engine = SagaEngine(gemini_api_key=settings.gemini_api_key, ip_geolocation_api_key=settings.ip_geolocation_api_key)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Saga slumbers.")
--- END OF FILE backend/server.py ---