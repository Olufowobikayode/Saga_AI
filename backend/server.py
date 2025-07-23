import os
import logging
from pathlib import Path
import uuid

from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional, List, Dict, Literal

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

# ### FIX: Consolidated and clarified Commerce Saga request models to match the unified stack.

class CommerceAuditRequest(BaseModel):
    prophecy_type: Literal["Commerce Audit"] = Field("Commerce Audit", description="The type of prophecy to invoke.")
    audit_type: Literal["Account Audit", "Store Audit", "Account Prediction"] = Field(..., examples=["Account Audit", "Store Audit"], description="The specific type of audit to perform.")
    statement_text: Optional[str] = Field(None, description="Pasted text from a TXT, CSV, or DOC file of account statements for 'Account Audit' or 'Account Prediction'.")
    store_url: Optional[str] = Field(None, description="URL of the user's store for 'Store Audit' or 'Account Prediction'.")

class ArbitragePathsRequest(BaseModel):
    prophecy_type: Literal["Arbitrage Paths"] = Field("Arbitrage Paths", description="The type of prophecy to invoke.")
    mode: Literal["User_Buys_User_Sells", "Saga_Buys_User_Sells", "User_Buys_Saga_Sells", "Saga_Buys_Saga_Sells"] = Field(..., description="The mode of arbitrage to analyze.")
    product_name: Optional[str] = Field(None, description="The product to find arbitrage for. Required for user-defined modes.")
    buy_from_url: Optional[str] = Field(None, description="The URL of the marketplace to buy from. Required for user-defined modes.")
    sell_on_url: Optional[str] = Field(None, description="The URL of the marketplace to sell on. Required for user-defined modes.")
    category: Optional[str] = Field(None, description="Optional product category to refine the search.")
    subcategory: Optional[str] = Field(None, description="Optional product subcategory to refine the search.")

class SocialSellingSagaRequest(BaseModel):
    prophecy_type: Literal["Social Selling Saga"] = Field("Social Selling Saga", description="The type of prophecy to invoke.")
    product_name: str = Field(..., description="The name of the product to create a saga for.")
    social_selling_price: float = Field(..., description="The target price to sell the product at on social media.")
    desired_profit_per_product: float = Field(..., description="The user's target profit per unit sold, after costs.")
    social_platform: str = Field("Instagram", description="The primary social platform for the campaign.")
    ads_daily_budget: float = Field(10.0, gt=4.99, lt=1000.01, description="The daily budget for social media ads.")
    product_category: Optional[str] = Field(None, description="Optional product category to refine the strategy.")
    product_subcategory: Optional[str] = Field(None, description="Optional product subcategory to refine the strategy.")

class ProductRouteRequest(BaseModel):
    prophecy_type: Literal["Product Route"] = Field("Product Route", description="The type of prophecy to invoke.")
    location_type: Literal["Global", "My Location"] = Field(..., description="The target market scope for the product route.")
    
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
    asset_type: Literal["Ad Copy", "Landing Page", "Email Copy", "Funnel Page", "Affiliate Copy"]

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

# ### FIX: Consolidated the four separate commerce endpoints into a single, unified endpoint.
# This aligns with the 'CommerceSagaStack' design and simplifies the API surface.

@api_router.post("/prophesy/commerce", response_model=SagaResponse, tags=["3. Commerce Prophecies"])
async def get_commerce_prophecy(request: CommerceAuditRequest | ArbitragePathsRequest | SocialSellingSagaRequest | ProductRouteRequest):
    """
    A unified endpoint for all commerce-related prophecies.
    - **Commerce Audit**: Performs an Account Audit, Store Audit, or Account Prediction.
    - **Arbitrage Paths**: Finds buy-low, sell-high opportunities based on one of four modes.
    - **Social Selling Saga**: Generates a complete social selling plan based on profit goals.
    - **Product Route**: Finds a high-profit-margin product to sell globally or locally.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Saga is slumbering.")
    
    request_data = request.model_dump()
    prophecy_type = request_data.pop("prophecy_type") # Extract prophecy type to pass to engine
    
    try:
        data = await engine.prophesy_commerce_saga(prophecy_type=prophecy_type, **request_data)
        return SagaResponse(prophecy_type=prophecy_type.lower().replace(" ", "_"), data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during commerce prophecy '{prophecy_type}': {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while divining the prophecy.")


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