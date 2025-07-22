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
class SagaResponse(BaseModel):
    prophecy_type: str
    data: Any

# --- Commerce Saga Models ---
class CommerceAuditRequest(BaseModel):
    audit_type: str = Field(..., examples=["Account Audit", "Store Audit", "Account Prediction"])
    statement_text: Optional[str] = Field(None, description="Pasted text from a TXT, CSV, or DOC file of account statements.")
    store_url: Optional[str] = Field(None, description="URL of the user's store for Store Audit and Prediction.")

class ArbitragePathsRequest(BaseModel):
    mode: str = Field(..., examples=["User_Buys_User_Sells", "Saga_Buys_User_Sells", "User_Buys_Saga_Sells", "Saga_Buys_Saga_Sells"])
    product_name: Optional[str] = None
    buy_from_url: Optional[str] = None
    sell_on_url: Optional[str] = None
    amount_to_buy: Optional[int] = None
    ads_daily_budget: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None

class SocialSellingSagaRequest(BaseModel):
    niche: str
    product_name: str
    social_platform: str
    social_selling_price: float
    ads_daily_budget: float = Field(..., gt=4.99, lt=1000.01)
    desired_profit_per_product: float
    product_category: Optional[str] = None
    product_subcategory: Optional[str] = None

class ProductRouteRequest(BaseModel):
    location_type: str = Field(..., examples=["Global", "My Location"])

# --- Other Stack Models ---
class GrandStrategyRequest(BaseModel):
    interest: str
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None
    user_ip_address: Optional[str] = None
    target_country_name: Optional[str] = None

class NewVentureRequest(GrandStrategyRequest):
    pass

class MarketingAnglesRequest(BaseModel):
    product_name: str
    product_description: str
    target_audience: str
    asset_type: str = Field(..., examples=["Ad Copy", "Landing Page", "Email Copy"])

class MarketingAssetRequest(BaseModel):
    marketing_session_id: str
    angle_id: str

class PODOpportunitiesRequest(BaseModel):
    niche_interest: str

class PODPackageRequest(BaseModel):
    pod_session_id: str
    concept_id: str

# --- FASTAPI APP AND ROUTER ---
app = FastAPI(title="Saga AI", version="10.0.0", description="The all-seeing, all-knowing Norse Goddess of Wisdom and Strategy, brought to life.")
api_router = APIRouter(prefix="/api/v10")
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

@api_router.post("/prophesy/grand-strategy", response_model=SagaResponse, tags=["2. Foundational Prophecies"])
async def get_grand_strategy(request: GrandStrategyRequest):
    """The mandatory first step for an existing venture. Returns a master plan and session_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_grand_strategy(**request.model_dump())
    return SagaResponse(prophecy_type="grand_strategy", data=data)

@api_router.post("/prophesy/new-venture-visions", response_model=SagaResponse, tags=["2. Foundational Prophecies"])
async def get_new_venture_visions(request: NewVentureRequest):
    """For broad interests. Generates 10 potential business ideas and a session_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_new_venture_visions(**request.model_dump())
    return SagaResponse(prophecy_type="new_venture_visions", data=data)

@api_router.post("/prophesy/commerce/audit", response_model=SagaResponse, tags=["3. Commerce Prophecies"])
async def get_commerce_audit(request: CommerceAuditRequest):
    """Performs an Account Audit, Store Audit, or Account Prediction."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_commerce_saga(prophecy_type="Commerce Audit", **request.model_dump())
    return SagaResponse(prophecy_type="commerce_audit", data=data)

@api_router.post("/prophesy/commerce/arbitrage-paths", response_model=SagaResponse, tags=["3. Commerce Prophecies"])
async def get_arbitrage_paths(request: ArbitragePathsRequest):
    """Finds buy-low, sell-high opportunities based on one of four modes."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_commerce_saga(prophecy_type="Arbitrage Paths", **request.model_dump())
    return SagaResponse(prophecy_type="arbitrage_paths", data=data)

@api_router.post("/prophesy/commerce/social-selling-saga", response_model=SagaResponse, tags=["3. Commerce Prophecies"])
async def get_social_selling_saga(request: SocialSellingSagaRequest):
    """Generates a complete social selling plan based on profit goals."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_commerce_saga(prophecy_type="Social Selling Saga", **request.model_dump())
    return SagaResponse(prophecy_type="social_selling_saga", data=data)

@api_router.post("/prophesy/commerce/product-route", response_model=SagaResponse, tags=["3. Commerce Prophecies"])
async def get_product_route(request: ProductRouteRequest):
    """Finds a high-profit-margin product to sell globally or locally."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_commerce_saga(prophecy_type="Product Route", **request.model_dump())
    return SagaResponse(prophecy_type="product_route", data=data)

@api_router.post("/prophesy/marketing/angles", response_model=SagaResponse, tags=["4. Marketing Prophecies"])
async def get_marketing_angles(request: MarketingAnglesRequest):
    """Phase 1: Research 2025 techniques & generate strategic 'angle cards'."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_marketing_angles(**request.model_dump())
    return SagaResponse(prophecy_type="marketing_angles", data=data)

@api_router.post("/prophesy/marketing/asset", response_model=SagaResponse, tags=["4. Marketing Prophecies"])
async def get_marketing_asset(request: MarketingAssetRequest):
    """Phase 2: Generate a final marketing asset from a chosen angle_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_marketing_asset(**request.model_dump())
        return SagaResponse(prophecy_type="marketing_asset", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized or invalid ID: {e}")

@api_router.post("/prophesy/pod/opportunities", response_model=SagaResponse, tags=["5. Print on Demand Prophecies"])
async def get_pod_opportunities(request: PODOpportunitiesRequest):
    """Phase 1: Researches a POD niche and generates strategic 'Design Concept' cards."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_pod_opportunities(**request.model_dump())
    return SagaResponse(prophecy_type="pod_opportunities", data=data)

@api_router.post("/prophesy/pod/package", response_model=SagaResponse, tags=["5. Print on Demand Prophecies"])
async def get_pod_package(request: PODPackageRequest):
    """Phase 2: Generates a complete design & listing package from a chosen concept_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_pod_design_package(**request.model_dump())
        return SagaResponse(prophecy_type="pod_design_package", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized or invalid ID: {e}")

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