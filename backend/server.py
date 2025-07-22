--- START OF FILE backend/server.py ---
import os
import logging
from pathlib import Path

from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional, List

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
    interest: Optional[str] = None # Optional now, as not all prophecies require it.
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

class SagaResponse(BaseModel):
    """The format for a prophecy sent back to the mortal realm."""
    prophecy_type: str
    data: Any

# --- FastAPI APP AND ROUTER ---
app = FastAPI(
    title="Saga AI",
    description="The digital throne of Saga, the Norse Goddess of Wisdom. This API is the gateway for solopreneurs to seek her prophetic counsel.",
    version="2.0.0"
)

api_router = APIRouter(prefix="/api/v2")

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

@api_router.post("/prophesy/new-ventures", response_model=SagaResponse, tags=["Prophecies"])
async def get_new_ventures_prophecy(request: SagaRequest):
    """Seek a Prophecy of Beginnings for a new business idea."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    if not request.interest: raise HTTPException(status_code=400, detail="An 'interest' is required for this prophecy.")
    
    logger.info(f"A mortal seeks a Prophecy of Beginnings for: {request.interest}")
    data = await engine.prophesy_new_ventures(**request.model_dump())
    return SagaResponse(prophecy_type="new_ventures", data=data)

@api_router.post("/prophesy/content-saga", response_model=SagaResponse, tags=["Prophecies"])
async def get_content_prophecy(request: SagaRequest):
    """Seek a Content Saga to build a following."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    if not request.interest: raise HTTPException(status_code=400, detail="An 'interest' is required for this prophecy.")
        
    logger.info(f"A mortal seeks a Content Saga for: {request.interest}")
    data = await engine.prophesy_content_saga(**request.model_dump())
    return SagaResponse(prophecy_type="content_saga", data=data)

@api_router.post("/prophesy/grand-strategy", response_model=SagaResponse, tags=["Prophecies"])
async def get_strategy_prophecy(request: SagaRequest):
    """Seek a Grand Strategy for market domination."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    if not request.interest: raise HTTPException(status_code=400, detail="An 'interest' is required for this prophecy.")

    logger.info(f"A mortal seeks a Grand Strategy for: {request.interest}")
    data = await engine.prophesy_grand_strategy(**request.model_dump())
    return SagaResponse(prophecy_type="grand_strategy", data=data)

@api_router.post("/prophesy/commerce-audit", response_model=SagaResponse, tags=["Prophecies"])
async def get_commerce_prophecy(request: SagaRequest):
    """Seek a Commerce Audit for a specific product."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    if not request.product_name: raise HTTPException(status_code=400, detail="A 'product_name' is required for this prophecy.")
        
    logger.info(f"A mortal seeks a Commerce Audit for: {request.product_name}")
    data = await engine.prophesy_commerce_audit(**request.model_dump())
    return SagaResponse(prophecy_type="commerce_audit", data=data)

@api_router.post("/prophesy/arbitrage-paths", response_model=SagaResponse, tags=["Prophecies"])
async def get_arbitrage_prophecy(request: SagaRequest):
    """Seek a Prophecy of Hidden Value between two marketplaces."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    if not all([request.product_name, request.buy_marketplace_link, request.sell_marketplace_link]):
        raise HTTPException(status_code=400, detail="This prophecy requires a 'product_name', 'buy_marketplace_link', and 'sell_marketplace_link'.")
    
    logger.info(f"A mortal seeks a Prophecy of Hidden Value for: '{request.product_name}'")
    data = await engine.prophesy_arbitrage_paths(**request.model_dump())
    return SagaResponse(prophecy_type="arbitrage_paths", data=data)

@api_router.post("/prophesy/social-selling-saga", response_model=SagaResponse, tags=["Prophecies"])
async def get_social_selling_prophecy(request: SagaRequest):
    """Seek a Social Selling Saga to master influence."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    if not all([request.product_name, request.product_selling_price is not None, request.social_platforms_to_sell, request.ads_daily_budget is not None, request.number_of_days is not None, request.amount_to_buy is not None]):
        raise HTTPException(status_code=400, detail="This prophecy requires full details of the product and campaign plan.")

    logger.info(f"A mortal seeks a Social Selling Saga for: '{request.product_name}'")
    data = await engine.prophesy_social_selling_saga(**request.model_dump())
    return SagaResponse(prophecy_type="social_selling_saga", data=data)

@api_router.post("/prophesy/product-route", response_model=SagaResponse, tags=["Prophecies"])
async def get_product_route_prophecy(request: SagaRequest):
    """Seek the Pathfinder's Prophecy to find a tangible product and its route to market."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    if not request.interest: raise HTTPException(status_code=400, detail="An 'interest' is required for this prophecy.")

    logger.info(f"A mortal seeks the Pathfinder's Prophecy for niche: '{request.interest}'")
    data = await engine.prophesy_product_route(**request.model_dump(exclude_none=True))
    return SagaResponse(prophecy_type="product_route", data=data)

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
    # ... [This startup logic remains unchanged from our last step]
    global db_client, database, engine, app_settings
    try:
        app_settings = Settings()
        logger.info("The sacred scrolls (settings) have been read.")
    except Exception as e:
        logger.critical(f"FATAL: The sacred scrolls are unreadable. Saga cannot awaken. Error: {e}")
        return
    if app_settings.mongo_uri:
        # Connect to MongoDB
        pass
    if app_settings.gemini_api_key:
        engine = SagaEngine(gemini_api_key=app_settings.gemini_api_key, ip_geolocation_api_key=app_settings.ip_geolocation_api_key)

@app.on_event("shutdown")
async def shutdown_event():
    # ... [This shutdown logic remains unchanged]
    pass
--- END OF FILE backend/server.py ---