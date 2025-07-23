# --- START OF FILE backend/server.py ---
import os
import logging
from pathlib import Path
import uuid
from datetime import datetime

from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional, List, Dict, Literal
from bson import ObjectId

from backend.engine import SagaEngine
from backend.marketplace_finder import MarketplaceScout
# SAGA GRIMOIRE: Import our new database modules
from backend.database import connect_to_mongo, close_mongo_connection, get_database
import motor.motor_asyncio

logger = logging.getLogger(__name__)

# --- CONFIGURATION SETTINGS ---
class Settings(BaseSettings):
    gemini_api_key: str
    mongo_uri: str
    # SAGA GRIMOIRE: A new secret key for protecting the admin endpoint.
    admin_api_key: str = Field(..., alias='ADMIN_API_KEY')
    ip_geolocation_api_key: Optional[str] = Field(None, alias='IP_GEOLOCATION_API_KEY')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- PYDANTIC MODELS ---

# Models for the existing Saga prophecies...
class SagaResponse(BaseModel): # ... and all other existing models
    prophecy_type: str
    data: Any
class CommerceAuditRequest(BaseModel):
    prophecy_type: Literal["Commerce Audit"]; audit_type: Literal["Account Audit", "Store Audit", "Account Prediction"]; statement_text: Optional[str] = None; store_url: Optional[str] = None
class ArbitragePathsRequest(BaseModel):
    prophecy_type: Literal["Arbitrage Paths"]; mode: Literal["User_Buys_User_Sells", "Saga_Buys_User_Sells", "User_Buys_Saga_Sells", "Saga_Buys_Saga_Sells"]; product_name: Optional[str] = None; buy_from_url: Optional[str] = None; sell_on_url: Optional[str] = None; category: Optional[str] = None; subcategory: Optional[str] = None
class SocialSellingSagaRequest(BaseModel):
    prophecy_type: Literal["Social Selling Saga"]; product_name: str; social_selling_price: float; desired_profit_per_product: float; social_platform: str = "Instagram"; ads_daily_budget: float = 10.0; product_category: Optional[str] = None; product_subcategory: Optional[str] = None
class ProductRouteRequest(BaseModel):
    prophecy_type: Literal["Product Route"]; location_type: Literal["Global", "My Location"]
class GrandStrategyRequest(BaseModel):
    interest: str; user_content_text: Optional[str] = None; user_content_url: Optional[str] = None; user_ip_address: Optional[str] = None; target_country_name: Optional[str] = None
class NewVentureRequest(GrandStrategyRequest): pass
class MarketingAnglesRequest(BaseModel):
    product_name: str; product_description: str; target_audience: str; asset_type: Literal["Ad Copy", "Landing Page", "Email Copy", "Funnel Page", "Affiliate Copy"]
class MarketingAssetRequest(BaseModel):
    marketing_session_id: str; angle_id: str
class PODOpportunitiesRequest(BaseModel):
    niche_interest: str
class PODPackageRequest(BaseModel):
    pod_session_id: str; concept_id: str

# SAGA GRIMOIRE: New Pydantic models for our blog posts.
class GrimoirePageBase(BaseModel):
    title: str
    slug: str
    author: str = "Saga"
    content: str # The main body of the article
    summary: str # A short summary for the card view
    tags: List[str] = []

    @validator('slug', pre=True, always=True)
    def generate_slug(cls, v, values):
        # Automatically create a URL-friendly slug from the title if not provided
        if not v:
            title = values.get('title', '')
            v = title.lower().replace(' ', '-').replace(':', '').replace('?', '')
        return v

class GrimoirePageCreate(GrimoirePageBase):
    pass

class GrimoirePageDB(GrimoirePageBase):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True


# --- FASTAPI APP AND ROUTER ---
app = FastAPI(title="Saga AI", version="11.0.0", description="The all-seeing Oracle of Strategy, now with an inscribed Grimoire of Wisdom.")
api_router = APIRouter(prefix="/api/v10")
engine: SagaEngine = None
scout: MarketplaceScout = None
settings = Settings() # Load settings once

# --- SAGA GRIMOIRE: Security Dependency ---
async def verify_admin_key(x_admin_api_key: str = Header(...)):
    """A dependency to protect our admin endpoint."""
    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Admin API Key")
    return True

# --- API ENDPOINTS ---

# Existing System and Prophecy endpoints...
@api_router.get("/health", tags=["1. System"]) # ... and all other existing endpoints
async def health_check(): return {"message": "Saga is conscious and the Bifrost to this API is open."}
@api_router.post("/discover-marketplaces", tags=["1. System"])
async def discover_marketplaces_endpoint(background_tasks: BackgroundTasks):
    if not scout: raise HTTPException(status_code=503, detail="Saga's Scout is not ready.")
    background_tasks.add_task(scout.find_general_marketplaces)
    return {"status": "Discovery mission launched."}
@api_router.post("/prophesy/grand-strategy", response_model=SagaResponse, tags=["2. Foundational Prophecies"])
async def get_grand_strategy(request: GrandStrategyRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_grand_strategy(**request.model_dump())
    return SagaResponse(prophecy_type="grand_strategy", data=data)
# ... all other prophecy endpoints ...

# SAGA GRIMOIRE: The new endpoints for our blog.
@api_router.post("/grimoire/inscribe", status_code=201, tags=["6. Saga Grimoire (Admin)"], dependencies=[Depends(verify_admin_key)])
async def create_grimoire_page(
    page: GrimoirePageCreate,
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)
):
    """
    (Admin Only) Inscribes a new page of wisdom into the Grimoire.
    """
    page_dict = page.model_dump()
    page_dict["created_at"] = datetime.utcnow()
    
    # Check if a page with this slug already exists to prevent duplicates
    if await db.grimoire_pages.find_one({"slug": page_dict["slug"]}):
        raise HTTPException(status_code=400, detail="A scroll with this slug already exists in the Grimoire.")
        
    result = await db.grimoire_pages.insert_one(page_dict)
    created_page = await db.grimoire_pages.find_one({"_id": result.inserted_id})
    return GrimoirePageDB.model_validate(created_page)

@api_router.get("/grimoire/scrolls", response_model=List[GrimoirePageDB], tags=["7. Saga Grimoire (Public)"])
async def get_all_grimoire_pages(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    """
    (Public) Retrieves all inscribed scrolls from the Grimoire, sorted by newest first.
    """
    pages_cursor = db.grimoire_pages.find().sort("created_at", -1)
    pages = await pages_cursor.to_list(length=100) # Limit to 100 scrolls for now
    return [GrimoirePageDB.model_validate(page) for page in pages]

@api_router.get("/grimoire/scrolls/{slug}", response_model=GrimoirePageDB, tags=["7. Saga Grimoire (Public)"])
async def get_grimoire_page_by_slug(slug: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    """
    (Public) Retrieves a single scroll from the Grimoire by its unique slug.
    """
    page = await db.grimoire_pages.find_one({"slug": slug})
    if page:
        return GrimoirePageDB.model_validate(page)
    raise HTTPException(status_code=404, detail=f"The scroll '{slug}' was not found in the Grimoire.")


# --- APP STARTUP & SHUTDOWN EVENTS ---
app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    global engine, scout
    if settings.gemini_api_key:
        engine = SagaEngine(gemini_api_key=settings.gemini_api_key, ip_geolocation_api_key=settings.ip_geolocation_api_key)
        scout = MarketplaceScout()
        # SAGA GRIMOIRE: Connect to the database on startup.
        await connect_to_mongo(settings.mongo_uri)
        logger.info("Saga's Engine, Scout, and Memory Scrolls are awake and ready.")
    else:
        logger.error("GEMINI_API_KEY not found. Saga cannot awaken.")

@app.on_event("shutdown")
async def shutdown_event():
    # SAGA GRIMOIRE: Disconnect from the database on shutdown.
    await close_mongo_connection()

# --- END OF FILE backend/server.py ---