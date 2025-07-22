--- START OF FILE backend/server.py ---
import os
import logging
from pathlib import Path

from fastapi import FastAPI, APIRouter, HTTPException, Request
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
    """
    The sacred scrolls that hold the secrets (environment variables) for the application.
    """
    gemini_api_key: str
    mongo_uri: str
    ip_geolocation_api_key: Optional[str] = Field(None, alias='IP_GEOLOCATION_API_KEY')

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- Pydantic Request/Response MODELS (The structure of mortal queries and divine prophecies) ---
class SagaRequest(BaseModel):
    """The format for a mortal's request for wisdom."""
    interest: Optional[str] = None
    product_name: Optional[str] = None
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None
    
    # Contextual data for the prophecy
    user_ip_address: Optional[str] = None
    target_country_name: Optional[str] = None
    product_category: Optional[str] = None
    product_subcategory: Optional[str] = None

    # Fields for the Commerce Audit & Social Selling Sagas
    user_store_url: Optional[str] = None
    marketplace_link: Optional[str] = None
    product_selling_price: Optional[float] = None
    social_platforms_to_sell: Optional[List[str]] = None
    ads_daily_budget: Optional[float] = None
    number_of_days: Optional[int] = None
    amount_to_buy: Optional[int] = None

    # Fields for the Arbitrage Prophecy
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

@api_router.post("/prophesy/idea-stack", response_model=SagaResponse, tags=["Prophecies"])
async def get_idea_prophecy(request: SagaRequest):
    """
    Seek a Prophecy of Beginnings. Saga will gaze into the threads of fate
    to discover and validate new business opportunities based on a mortal's interest.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Saga is slumbering. The AI Engine is not available.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="A mortal must provide an 'interest' to receive a Prophecy of Beginnings.")
    
    logger.info(f"A mortal seeks a Prophecy of Beginnings for: {request.interest}")
    # The server cleanly calls the high-level engine method.
    data = await engine.prophesy_new_ventures(
        interest=request.interest,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory
    )
    return SagaResponse(prophecy_type="idea_stack", data=data)

@api_router.post("/prophesy/content-stack", response_model=SagaResponse, tags=["Prophecies"])
async def get_content_prophecy(request: SagaRequest):
    """
    Seek a Content Saga. Saga will divine a foundational set of content ideas
    (blog posts, video concepts) to help a mortal build a following.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Saga is slumbering. The AI Engine is not available.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="A mortal must provide an 'interest' to receive a Content Saga.")
        
    logger.info(f"A mortal seeks a Content Saga for: {request.interest}")
    data = await engine.run_content_stack(
        interest=request.interest,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory
    )
    return SagaResponse(prophecy_type="content_stack", data=data)

@api_router.post("/prophesy/commerce-stack", response_model=SagaResponse, tags=["Prophecies"])
async def get_commerce_prophecy(request: SagaRequest):
    """
    Seek a Commerce Audit. Saga will perform a deep divination of a specific
    product's market viability, profitability, and strategic positioning.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Saga is slumbering. The AI Engine is not available.")
    if not request.product_name:
        raise HTTPException(status_code=400, detail="A mortal must provide a 'product_name' for a Commerce Audit.")
        
    logger.info(f"A mortal seeks a Commerce Audit for: {request.product_name}")
    data = await engine.run_commerce_stack(
        product_name=request.product_name,
        user_tone_instruction=await engine._get_user_tone_instruction(request.user_content_text, request.user_content_url),
        target_country_code=(await engine._resolve_country_context(request.user_ip_address, request.target_country_name))['country_code'],
        country_name_for_ai=(await engine._resolve_country_context(request.user_ip_address, request.target_country_name))['country_name'],
        is_global_search=(await engine._resolve_country_context(request.user_ip_address, request.target_country_name))['is_global'],
        user_store_url=request.user_store_url,
        marketplace_link=request.marketplace_link,
        product_selling_price=request.product_selling_price,
        social_platforms_to_sell=request.social_platforms_to_sell,
        ads_daily_budget=request.ads_daily_budget,
        number_of_days=request.number_of_days,
        amount_to_buy=request.amount_to_buy
    )
    return SagaResponse(prophecy_type="commerce_stack", data=data)

@api_router.post("/prophesy/arbitrage-stack", response_model=SagaResponse, tags=["Prophecies"])
async def get_arbitrage_prophecy(request: SagaRequest):
    """
    Seek a Prophecy of Hidden Value. Saga will divine buy-low, sell-high
    opportunities between two specified marketplaces.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Saga is slumbering. The AI Engine is not available.")
    if not all([request.product_name, request.buy_marketplace_link, request.sell_marketplace_link]):
        raise HTTPException(status_code=400, detail="For a Prophecy of Hidden Value, you must provide a 'product_name', 'buy_marketplace_link', and 'sell_marketplace_link'.")
    
    logger.info(f"A mortal seeks a Prophecy of Hidden Value for: '{request.product_name}'")
    data = await engine.run_arbitrage_stack(
        product_name=request.product_name,
        buy_marketplace_link=request.buy_marketplace_link,
        sell_marketplace_link=request.sell_marketplace_link,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory
    )
    return SagaResponse(prophecy_type="arbitrage_stack", data=data)

@api_router.post("/prophesy/social-selling-stack", response_model=SagaResponse, tags=["Prophecies"])
async def get_social_selling_prophecy(request: SagaRequest):
    """
    Seek a Social Selling Saga. Saga will devise a strategy to sell a product
    through the power of community and influence on social platforms.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Saga is slumbering. The AI Engine is not available.")
    if not all([request.product_name, request.product_selling_price is not None, request.social_platforms_to_sell, request.ads_daily_budget is not None, request.number_of_days is not None, request.amount_to_buy is not None]):
        raise HTTPException(status_code=400, detail="To receive a Social Selling Saga, many fields are required, including 'product_name', 'product_selling_price', and details of the planned campaign.")

    logger.info(f"A mortal seeks a Social Selling Saga for: '{request.product_name}'")
    data = await engine.run_social_selling_stack(
        product_name=request.product_name,
        product_selling_price=request.product_selling_price,
        social_platforms_to_sell=request.social_platforms_to_sell,
        ads_daily_budget=request.ads_daily_budget,
        number_of_days=request.number_of_days,
        amount_to_buy=request.amount_to_buy,
        supplier_marketplace_link=request.marketplace_link,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory
    )
    return SagaResponse(prophecy_type="social_selling_stack", data=data)

@api_router.post("/prophesy/product-route-stack", response_model=SagaResponse, tags=["Prophecies"])
async def get_product_route_prophecy(request: SagaRequest):
    """
    Seek the Pathfinder's Prophecy. Saga will divine a complete route from a
    niche interest to a specific, tangible product with a sourcing and selling plan.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Saga is slumbering. The AI Engine is not available.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="A mortal must provide an 'interest' to receive the Pathfinder's Prophecy.")

    logger.info(f"A mortal seeks the Pathfinder's Prophecy for niche: '{request.interest}'")
    data = await engine.run_product_route_stack(
        niche_interest=request.interest,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory
    )
    return SagaResponse(prophecy_type="product_route_stack", data=data)

# --- Final App Configuration ---
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In a true production environment, this should be restricted to the frontend's domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- The Awakening and Slumbering of the Engine ---
@app.on_event("startup")
async def startup_event():
    """
    The grand ritual of awakening. Connects to the database and breathes life into the SagaEngine.
    """
    global db_client, database, engine, app_settings

    try:
        app_settings = Settings()
        logger.info("The sacred scrolls (settings) have been read.")
    except Exception as e:
        logger.critical(f"FATAL: The sacred scrolls are unreadable. Saga cannot awaken. Ensure .env is configured. Error: {e}")
        app_settings = None
        return

    if app_settings.mongo_uri:
        try:
            db_client = AsyncIOMotorClient(app_settings.mongo_uri)
            database = db_client.get_database("saga_ai_db")
            await database.command("ping")
            logger.info("A connection to the great database of histories, MongoDB, has been established.")
        except Exception as e:
            logger.error(f"Could not connect to the database of histories. Saga's memory will be fleeting. Error: {e}")
            db_client = None
            database = None
    else:
        logger.warning("No MongoDB URI found in the scrolls. Saga's memory will be fleeting.")

    if app_settings.gemini_api_key:
        try:
            engine = SagaEngine(
                gemini_api_key=app_settings.gemini_api_key,
                ip_geolocation_api_key=app_settings.ip_geolocation_api_key
            )
        except Exception as e:
            logger.critical(f"FATAL: The SagaEngine could not be brought to consciousness! Error: {e}")
            engine = None
    else:
        logger.critical("FATAL: The Gemini API Key, the very source of prophetic power, is missing. Saga cannot awaken.")
        engine = None

@app.on_event("shutdown")
async def shutdown_event():
    """The rite of slumber. The SagaEngine rests."""
    global db_client
    if db_client:
        db_client.close()
        logger.info("The connection to the database of histories has been closed. Saga slumbers.")
--- END OF FILE backend/server.py ---