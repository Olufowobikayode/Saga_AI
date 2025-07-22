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

from backend.engine import SagaEngine
from backend.marketplace_finder import MarketplaceScout

logger = logging.getLogger(__name__)

# --- CONFIGURATION SETTINGS ---
class Settings(BaseSettings):
    gemini_api_key: str
    mongo_uri: str
    ip_geolocation_api_key: Optional[str] = Field(None, alias='IP_GEOLOCATION_API_KEY')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- PYDANTIC MODELS: Defining the structure of requests and responses ---
class SagaBaseRequest(BaseModel):
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None
    user_ip_address: Optional[str] = None
    target_country_name: Optional[str] = None

class GrandStrategyRequest(SagaBaseRequest):
    interest: str

class NewVentureRequest(SagaBaseRequest):
    interest: str

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

class SocialSellingRequest(BaseModel):
    strategy_session_id: str
    product_name: str
    product_selling_price: float
    social_platforms_to_sell: List[str]
    ads_daily_budget: float
    number_of_days: int
    amount_to_buy: int
    supplier_marketplace_link: Optional[str] = None

class ProductRouteRequest(BaseModel):
    strategy_session_id: str
    niche_interest: str

class MarketingAnglesRequest(BaseModel):
    product_name: str
    product_description: str
    target_audience: str
    asset_type: str = Field(..., description="Asset type to get angles for.", examples=["Ad Copy", "Landing Page", "Email Copy", "Affiliate Copy", "Funnel Page"])

class MarketingAssetRequest(BaseModel):
    marketing_session_id: str = Field(..., description="The session ID received from the marketing angles prophecy.")
    angle_id: str = Field(..., description="The unique ID of the angle card chosen from the marketing angles prophecy.")

class PODOpportunitiesRequest(BaseModel):
    niche_interest: str

class PODPackageRequest(BaseModel):
    pod_session_id: str = Field(..., description="The session ID received from the POD opportunities prophecy.")
    concept_id: str = Field(..., description="The unique ID of the design concept card chosen.")

class SagaResponse(BaseModel):
    prophecy_type: str
    data: Any

# --- FASTAPI APP AND ROUTER ---
app = FastAPI(title="Saga AI", version="9.0.0", description="The all-seeing, all-knowing Norse Goddess of Wisdom and Strategy, brought to life.")
api_router = APIRouter(prefix="/api/v9")
engine: SagaEngine = None
scout: MarketplaceScout = None

# --- API ENDPOINTS ---
@api_router.get("/health", tags=["1. System"])
async def health_check():
    return {"message": "Saga is conscious and the Bifrost to this API is open."}

@api_router.post("/discover-marketplaces", tags=["1. System"])
async def discover_marketplaces_endpoint(background_tasks: BackgroundTasks):
    """Commands Saga's scout to search for new marketplaces in the background."""
    if not scout: raise HTTPException(status_code=503, detail="Saga's Scout is not ready.")
    background_tasks.add_task(scout.find_general_marketplaces)
    return {"status": "Discovery mission launched."}

@api_router.post("/prophesy/grand-strategy", response_model=SagaResponse, tags=["2. Strategic Prophecies"])
async def get_grand_strategy(request: GrandStrategyRequest):
    """The mandatory first step for an existing venture. Returns a master plan and session_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_grand_strategy(**request.model_dump())
    return SagaResponse(prophecy_type="grand_strategy", data=data)

@api_router.post("/prophesy/new-venture-visions", response_model=SagaResponse, tags=["2. Strategic Prophecies"])
async def get_new_venture_visions(request: NewVentureRequest):
    """For broad interests. Generates 10 potential business ideas and a session_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_new_venture_visions(**request.model_dump())
    return SagaResponse(prophecy_type="new_venture_visions", data=data)

@api_router.post("/prophesy/marketing/angles", response_model=SagaResponse, tags=["3. Marketing Prophecies"])
async def get_marketing_angles(request: MarketingAnglesRequest):
    """Phase 1: Research 2025 techniques & generate strategic 'angle cards'."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_marketing_angles(**request.model_dump())
    return SagaResponse(prophecy_type="marketing_angles", data=data)

@api_router.post("/prophesy/marketing/asset", response_model=SagaResponse, tags=["3. Marketing Prophecies"])
async def get_marketing_asset(request: MarketingAssetRequest):
    """Phase 2: Generate a final marketing asset from a chosen angle_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_marketing_asset(**request.model_dump())
        return SagaResponse(prophecy_type="marketing_asset", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized or invalid ID: {e}")

@api_router.post("/prophesy/pod/opportunities", response_model=SagaResponse, tags=["4. Print on Demand Prophecies"])
async def get_pod_opportunities(request: PODOpportunitiesRequest):
    """Phase 1: Researches a POD niche and generates strategic 'Design Concept' cards."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_pod_opportunities(**request.model_dump())
    return SagaResponse(prophecy_type="pod_opportunities", data=data)

@api_router.post("/prophesy/pod/package", response_model=SagaResponse, tags=["4. Print on Demand Prophecies"])
async def get_pod_package(request: PODPackageRequest):
    """Phase 2: Generates a complete design & listing package from a chosen concept_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_pod_design_package(**request.model_dump())
        return SagaResponse(prophecy_type="pod_design_package", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized or invalid ID: {e}")

@api_router.post("/prophesy/ecommerce-audit", response_model=SagaResponse, tags=["5. Commerce Prophecies (Requires Strategy Session)"])
async def get_ecommerce_audit(request: EcommerceAuditRequest):
    """Performs a full business audit. Requires a valid strategy_session_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try: return SagaResponse(prophecy_type="ecommerce_audit", data=await engine.prophesy_ecommerce_audit(**request.model_dump()))
    except ValueError as e: raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

@api_router.post("/prophesy/price-arbitrage", response_model=SagaResponse, tags=["5. Commerce Prophecies (Requires Strategy Session)"])
async def get_price_arbitrage(request: PriceArbitrageRequest):
    """Finds buy-low, sell-high opportunities. Requires a valid strategy_session_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try: return SagaResponse(prophecy_type="price_arbitrage", data=await engine.prophesy_price_arbitrage(**request.model_dump()))
    except ValueError as e: raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

@api_router.post("/prophesy/social-selling", response_model=SagaResponse, tags=["5. Commerce Prophecies (Requires Strategy Session)"])
async def get_social_selling_strategy(request: SocialSellingRequest):
    """Creates a social media sales plan. Requires a valid strategy_session_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try: return SagaResponse(prophecy_type="social_selling_strategy", data=await engine.prophesy_social_selling(**request.model_dump()))
    except ValueError as e: raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

@api_router.post("/prophesy/product-route", response_model=SagaResponse, tags=["5. Commerce Prophecies (Requires Strategy Session)"])
async def get_product_route(request: ProductRouteRequest):
    """Finds a new product idea and its path to market. Requires a valid strategy_session_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try: return SagaResponse(prophecy_type="product_route", data=await engine.prophesy_product_route(**request.model_dump()))
    except ValueError as e: raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

# --- APP STARTUP & CONFIGURATION ---
app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

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
--- END OF FILE backend/server.py ---