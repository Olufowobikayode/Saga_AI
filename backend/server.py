--- START OF FILE backend/server.py ---
import os
import logging
from pathlib import Path
import uuid

from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional, List, Dict

# --- IMPORT THE MASTER ENGINE AND THE NEW SCOUT ---
from backend.engine import SagaEngine
from backend.marketplace_finder import MarketplaceScout

logger = logging.getLogger(__name__)

# --- CONFIGURATION SETTINGS (Unchanged) ---
class Settings(BaseSettings):
    gemini_api_key: str
    mongo_uri: str
    ip_geolocation_api_key: Optional[str] = Field(None, alias='IP_GEOLOCATION_API_KEY')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- Pydantic Models ---

# Base models for user context
class SagaBaseRequest(BaseModel):
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None
    user_ip_address: Optional[str] = None
    target_country_name: Optional[str] = None

# Models for specific prophecies
class GrandStrategyRequest(SagaBaseRequest):
    interest: str

class ContentSparksRequest(BaseModel):
    strategy_session_id: str
    tactical_interest: str # Comes from a pillar in the Grand Strategy
    link: Optional[str] = None
    link_description: Optional[str] = None

# --- NEW: Request models for the newly exposed commerce prophecies ---
class EcommerceAuditRequest(BaseModel):
    strategy_session_id: str
    product_name: str
    user_store_url: Optional[str] = None
    marketplace_link: Optional[str] = None
    product_selling_price: Optional[float] = None
    social_platforms_to_sell: Optional[List[str]] = None
    ads_daily_budget: Optional[float] = 10.0
    number_of_days: Optional[int] = 30
    amount_to_buy: Optional[int] = None

class PriceArbitrageRequest(BaseModel):
    strategy_session_id: str
    product_name: str
    buy_marketplace_link: str
    sell_marketplace_link: str
    product_category: Optional[str] = None
    product_subcategory: Optional[str] = None

class SocialSellingRequest(BaseModel):
    strategy_session_id: str
    product_name: str
    product_selling_price: float
    social_platforms_to_sell: List[str]
    ads_daily_budget: float
    number_of_days: int
    amount_to_buy: int
    supplier_marketplace_link: Optional[str] = None
    product_category: Optional[str] = None
    product_subcategory: Optional[str] = None

class ProductRouteRequest(BaseModel):
    strategy_session_id: str
    niche_interest: str
    product_category: Optional[str] = None
    product_subcategory: Optional[str] = None

class SagaResponse(BaseModel):
    prophecy_type: str
    data: Any

# --- FastAPI APP AND ROUTER ---
app = FastAPI(
    title="Saga AI",
    description="The digital throne of Saga, the Norse Goddess of Wisdom.",
    version="6.0.0" # Version bump for major enhancements
)
api_router = APIRouter(prefix="/api/v6")
engine: SagaEngine = None
scout: MarketplaceScout = None


# --- API HEALTH CHECK & DISCOVERY ---
@api_router.get("/health", tags=["1. System & Discovery"])
async def health_check():
    return {"message": "Saga is conscious and the Bifrost to this API is open."}

@api_router.post("/discover-general-marketplaces", tags=["1. System & Discovery"])
async def discover_marketplaces_endpoint(background_tasks: BackgroundTasks):
    """
    Commands Saga's scout to search the web for new e-commerce marketplaces.
    This is a long-running task that will run in the background.
    """
    logger.info("A command has been issued to discover new general realms of commerce.")
    if not scout: raise HTTPException(status_code=503, detail="Saga's Scout is not ready.")
    
    # Run the discovery task in the background to avoid blocking the server
    background_tasks.add_task(scout.find_general_marketplaces)
    
    return {"status": "Discovery mission launched", "message": "The scout will update its knowledge base in the background."}


# --- PROPHECY ENDPOINTS ---

@api_router.post("/prophesy/grand-strategy", response_model=SagaResponse, tags=["2. Grand Strategy (Start Here)"])
async def get_grand_strategy(request: GrandStrategyRequest):
    """
    The mandatory first step. Provide an interest to receive a master plan and a
    'strategy_session_id' required for all other prophecies.
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_grand_strategy(**request.model_dump())
    return SagaResponse(prophecy_type="grand_strategy", data=data)

@api_router.post("/prophesy/content-saga/sparks", response_model=SagaResponse, tags=["3. Tactical Prophecies (Content)"])
async def get_content_sparks(request: ContentSparksRequest):
    """
    Phase 1 of the Content Saga. Provide a 'tactical_interest' from a Grand Strategy pillar
    to generate 5 actionable content ideas ("sparks").
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_content_sparks(**request.model_dump())
        return SagaResponse(prophecy_type="content_sparks", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

# ... (Other content-specific endpoints like social post, comment, etc. would follow here) ...

# --- NEW: Endpoints for all of Saga's Commerce abilities ---

@api_router.post("/prophesy/ecommerce-audit", response_model=SagaResponse, tags=["4. Tactical Prophecies (Commerce & Products)"])
async def get_ecommerce_audit(request: EcommerceAuditRequest):
    """
    Commands the Ecommerce Audit Analyzer to produce a full business audit.
    Requires a valid 'strategy_session_id'.
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        # The session ID is part of the request model and will be passed via **request.model_dump()
        data = await engine.prophesy_ecommerce_audit(**request.model_dump())
        return SagaResponse(prophecy_type="ecommerce_audit", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")
    except Exception as e:
        logger.error(f"Ecommerce audit prophecy failed: {e}")
        raise HTTPException(status_code=500, detail="The audit prophecy could not be completed.")

@api_router.post("/prophesy/price-arbitrage", response_model=SagaResponse, tags=["4. Tactical Prophecies (Commerce & Products)"])
async def get_price_arbitrage(request: PriceArbitrageRequest):
    """
    Commands the Price Arbitrage Finder to identify buy-low, sell-high opportunities.
    Requires a valid 'strategy_session_id'.
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_price_arbitrage(**request.model_dump())
        return SagaResponse(prophecy_type="price_arbitrage", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")
    except Exception as e:
        logger.error(f"Price arbitrage prophecy failed: {e}")
        raise HTTPException(status_code=500, detail="The arbitrage prophecy could not be completed.")

@api_router.post("/prophesy/social-selling", response_model=SagaResponse, tags=["4. Tactical Prophecies (Commerce & Products)"])
async def get_social_selling_strategy(request: SocialSellingRequest):
    """
    Commands the Social Selling Strategist to create a complete social media sales plan.
    Requires a valid 'strategy_session_id'.
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_social_selling(**request.model_dump())
        return SagaResponse(prophecy_type="social_selling_strategy", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")
    except Exception as e:
        logger.error(f"Social selling prophecy failed: {e}")
        raise HTTPException(status_code=500, detail="The social selling prophecy could not be completed.")

@api_router.post("/prophesy/product-route", response_model=SagaResponse, tags=["4. Tactical Prophecies (Commerce & Products)"])
async def get_product_route(request: ProductRouteRequest):
    """
    Commands the Product Route Suggester to find a new product idea and its path to market.
    Requires a valid 'strategy_session_id'.
    """
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_product_route(**request.model_dump())
        return SagaResponse(prophecy_type="product_route", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")
    except Exception as e:
        logger.error(f"Product route prophecy failed: {e}")
        raise HTTPException(status_code=500, detail="The product route prophecy could not be completed.")

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
    global engine, scout
    settings = Settings()
    if settings.gemini_api_key:
        engine = SagaEngine(gemini_api_key=settings.gemini_api_key, ip_geolocation_api_key=settings.ip_geolocation_api_key)
        scout = MarketplaceScout()
        logger.info("Saga's Engine and Scout are awake and ready.")
    else:
        logger.error("GEMINI_API_KEY not found. Saga cannot awaken.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Saga slumbers.")
--- END OF FILE backend/server.py ---