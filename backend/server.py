# --- START OF FILE backend/server.py ---
import os
import logging
from pathlib import Path
import uuid
from datetime import datetime
import re

from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional, List, Dict, Literal
from bson import ObjectId

from backend.engine import SagaEngine
from backend.marketplace_finder import MarketplaceScout
from backend.database import connect_to_mongo, close_mongo_connection, get_database
import motor.motor_asyncio

logger = logging.getLogger(__name__)

# --- CONFIGURATION SETTINGS ---
class Settings(BaseSettings):
    gemini_api_key: str
    mongo_uri: str
    admin_api_key: str = Field(..., alias='ADMIN_API_KEY')
    ip_geolocation_api_key: Optional[str] = Field(None, alias='IP_GEOLOCATION_API_KEY')
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- PYDANTIC MODELS ---
class SagaResponse(BaseModel):
    prophecy_type: str
    data: Any

class CommerceAuditRequest(BaseModel):
    prophecy_type: Literal["Commerce Audit"] = Field("Commerce Audit")
    audit_type: Literal["Account Audit", "Store Audit", "Account Prediction"]
    statement_text: Optional[str] = None
    store_url: Optional[str] = None

class ArbitragePathsRequest(BaseModel):
    prophecy_type: Literal["Arbitrage Paths"] = Field("Arbitrage Paths")
    mode: Literal["User_Buys_User_Sells", "Saga_Buys_User_Sells", "User_Buys_Saga_Sells", "Saga_Buys_Saga_Sells"]
    product_name: Optional[str] = None
    buy_from_url: Optional[str] = None
    sell_on_url: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None

class SocialSellingSagaRequest(BaseModel):
    prophecy_type: Literal["Social Selling Saga"] = Field("Social Selling Saga")
    product_name: str; social_selling_price: float; desired_profit_per_product: float
    social_platform: str = "Instagram"; ads_daily_budget: float = 10.0
    product_category: Optional[str] = None; product_subcategory: Optional[str] = None

class ProductRouteRequest(BaseModel):
    prophecy_type: Literal["Product Route"] = Field("Product Route")
    location_type: Literal["Global", "My Location"]

class AssetInfo(BaseModel):
    type: Optional[str] = None; name: Optional[str] = None; description: Optional[str] = None; promo_link: Optional[str] = None

class GrandStrategyRequest(BaseModel):
    interest: str; sub_niche: Optional[str] = None; user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None; target_country_name: Optional[str] = None
    asset_info: Optional[AssetInfo] = None

class NewVentureRequest(GrandStrategyRequest): pass

class NewVentureBlueprintRequest(BaseModel):
    venture_session_id: str
    vision_id: str

class MarketingAnglesRequest(BaseModel):
    product_name: str; product_description: str; target_audience: str
    asset_type: Literal["Ad Copy", "Landing Page", "Email Copy", "Funnel Page", "Affiliate Copy"]

class MarketingAssetRequest(BaseModel):
    marketing_session_id: str; angle_id: str
    platform: Optional[str] = None
    length: Optional[str] = None

class PODOpportunitiesRequest(BaseModel):
    niche_interest: str
class PODPackageRequest(BaseModel):
    pod_session_id: str; concept_id: str

class GrimoirePageBase(BaseModel):
    title: str; slug: str; author: str = "Saga"; content: str; summary: str; tags: List[str] = []
    @validator('slug', pre=True, always=True)
    def generate_slug(cls, v, values):
        if not v:
            title = values.get('title', '')
            s = title.lower().strip(); s = re.sub(r'[\s\W-]+', '-', s); v = s.strip('-')
        return v
class GrimoirePageCreate(GrimoirePageBase): pass
class GrimoirePageUpdate(BaseModel):
    title: Optional[str] = None; slug: Optional[str] = None; content: Optional[str] = None
    summary: Optional[str] = None; tags: Optional[List[str]] = None
class GrimoirePageDB(GrimoirePageBase):
    id: str = Field(..., alias="_id"); created_at: datetime = Field(default_factory=datetime.utcnow)
    class Config: json_encoders = {ObjectId: str}; allow_population_by_field_name = True

class TopicRequest(BaseModel): topic: str
class TitleRequest(BaseModel): title: str; topic: str

# --- FASTAPI APP AND ROUTER ---
app = FastAPI(title="Saga AI", version="12.0.0", description="The Oracle of Strategy, with a fully empowered Grimoire and Scriptorium.")
api_router = APIRouter(prefix="/api/v10")
engine: SagaEngine = None
scout: MarketplaceScout = None
settings = Settings()

# --- Security Dependency ---
async def verify_admin_key(x_admin_api_key: str = Header(...)):
    if x_admin_api_key != settings.admin_api_key: raise HTTPException(status_code=401, detail="Unauthorized")

# --- API ENDPOINTS ---
@api_router.get("/health", tags=["1. System"])
async def health_check(): return {"message": "Saga is conscious and the Bifrost to this API is open."}

@api_router.post("/discover-marketplaces", tags=["1. System"])
async def discover_marketplaces_endpoint(background_tasks: BackgroundTasks):
    if not scout: raise HTTPException(status_code=503, detail="Saga's Scout is not ready.")
    background_tasks.add_task(scout.find_general_marketplaces)
    return {"status": "Discovery mission launched."}

@api_router.post("/prophesy/grand-strategy", response_model=SagaResponse, tags=["2. Foundational Prophecies"])
async def get_grand_strategy(request: GrandStrategyRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_grand_strategy(**request.model_dump(exclude_unset=True))
    return SagaResponse(prophecy_type="grand_strategy", data=data)

@api_router.post("/prophesy/new-venture-visions", response_model=SagaResponse, tags=["2. Foundational Prophecies"])
async def get_new_venture_visions(request: NewVentureRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_new_venture_visions(**request.model_dump(exclude_unset=True))
    return SagaResponse(prophecy_type="new_venture_visions", data=data)

@api_router.post("/prophesy/new-venture-blueprint", response_model=SagaResponse, tags=["2. Foundational Prophecies"])
async def get_new_venture_blueprint(request: NewVentureBlueprintRequest):
    """Phase 2: Generate a final business blueprint from a chosen vision_id."""
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_venture_blueprint(**request.model_dump())
        return SagaResponse(prophecy_type="new_venture_blueprint", data=data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized or invalid ID: {e}")

@api_router.post("/prophesy/commerce", response_model=SagaResponse, tags=["3. Commerce Prophecies"])
async def get_commerce_prophecy(request: CommerceAuditRequest | ArbitragePathsRequest | SocialSellingSagaRequest | ProductRouteRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    request_data = request.model_dump(); prophecy_type = request_data.pop("prophecy_type")
    try:
        data = await engine.prophesy_commerce_saga(prophecy_type=prophecy_type, **request_data)
        return SagaResponse(prophecy_type=prophecy_type.lower().replace(" ", "_"), data=data)
    except ValueError as e: raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during commerce prophecy '{prophecy_type}': {e}"); raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@api_router.post("/prophesy/marketing/angles", response_model=SagaResponse, tags=["4. Marketing Prophecies"])
async def get_marketing_angles(request: MarketingAnglesRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_marketing_angles(**request.model_dump())
    return SagaResponse(prophecy_type="marketing_angles", data=data)

@api_router.post("/prophesy/marketing/asset", response_model=SagaResponse, tags=["4. Marketing Prophecies"])
async def get_marketing_asset(request: MarketingAssetRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_marketing_asset(**request.model_dump(exclude_unset=True))
        return SagaResponse(prophecy_type="marketing_asset", data=data)
    except ValueError as e: raise HTTPException(status_code=401, detail=f"Unauthorized or invalid ID: {e}")

@api_router.post("/prophesy/pod/opportunities", response_model=SagaResponse, tags=["5. Print on Demand Prophecies"])
async def get_pod_opportunities(request: PODOpportunitiesRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    data = await engine.prophesy_pod_opportunities(**request.model_dump())
    return SagaResponse(prophecy_type="pod_opportunities", data=data)

@api_router.post("/prophesy/pod/package", response_model=SagaResponse, tags=["5. Print on Demand Prophecies"])
async def get_pod_package(request: PODPackageRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    try:
        data = await engine.prophesy_pod_design_package(**request.model_dump())
        return SagaResponse(prophecy_type="pod_design_package", data=data)
    except ValueError as e: raise HTTPException(status_code=401, detail=f"Unauthorized or invalid ID: {e}")

# --- SAGA GRIMOIRE ADMIN ENDPOINTS ---
@api_router.post("/grimoire/generate-titles", tags=["6. Saga Grimoire (Admin)"], dependencies=[Depends(verify_admin_key)])
async def generate_grimoire_titles(request: TopicRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    return await engine.content_saga_stack.prophesy_title_slug_concepts(request.topic)

@api_router.post("/grimoire/generate-content", tags=["6. Saga Grimoire (Admin)"], dependencies=[Depends(verify_admin_key)])
async def generate_grimoire_content(request: TitleRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    return await engine.content_saga_stack.prophesy_full_scroll_content(request.title, request.topic)

@api_router.post("/grimoire/inscribe", status_code=201, response_model=GrimoirePageDB, tags=["6. Saga Grimoire (Admin)"], dependencies=[Depends(verify_admin_key)])
async def create_grimoire_page(page: GrimoirePageCreate, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    page_dict = page.model_dump(); page_dict["created_at"] = datetime.utcnow()
    if await db.grimoire_pages.find_one({"slug": page_dict["slug"]}):
        raise HTTPException(status_code=400, detail="A scroll with this slug already exists.")
    result = await db.grimoire_pages.insert_one(page_dict)
    created_page = await db.grimoire_pages.find_one({"_id": result.inserted_id})
    return GrimoirePageDB.model_validate(created_page)

@api_router.put("/grimoire/scrolls/{id}", response_model=GrimoirePageDB, tags=["6. Saga Grimoire (Admin)"], dependencies=[Depends(verify_admin_key)])
async def update_grimoire_page(id: str, page_update: GrimoirePageUpdate, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    update_data = page_update.model_dump(exclude_unset=True)
    if not update_data: raise HTTPException(status_code=400, detail="No update data provided.")
    if "slug" in update_data and await db.grimoire_pages.find_one({"slug": update_data["slug"], "_id": {"$ne": ObjectId(id)}}):
        raise HTTPException(status_code=400, detail="Another scroll with this slug already exists.")
    await db.grimoire_pages.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    updated_page = await db.grimoire_pages.find_one({"_id": ObjectId(id)})
    if updated_page: return GrimoirePageDB.model_validate(updated_page)
    raise HTTPException(status_code=404, detail=f"The scroll with id '{id}' could not be updated.")

@api_router.delete("/grimoire/scrolls/{id}", status_code=204, tags=["6. Saga Grimoire (Admin)"], dependencies=[Depends(verify_admin_key)])
async def delete_grimoire_page(id: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    delete_result = await db.grimoire_pages.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"The scroll with id '{id}' was not found.")

# --- SAGA GRIMOIRE PUBLIC ENDPOINTS ---
@api_router.get("/grimoire/scrolls", response_model=List[GrimoirePageDB], tags=["7. Saga Grimoire (Public)"])
async def get_all_grimoire_pages(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    pages_cursor = db.grimoire_pages.find().sort("created_at", -1)
    pages = await pages_cursor.to_list(length=100)
    return [GrimoirePageDB.model_validate(page) for page in pages]

@api_router.get("/grimoire/scrolls/{slug}", response_model=GrimoirePageDB, tags=["7. Saga Grimoire (Public)"])
async def get_grimoire_page_by_slug(slug: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    page = await db.grimoire_pages.find_one({"slug": slug})
    if page: return GrimoirePageDB.model_validate(page)
    raise HTTPException(status_code=404, detail=f"The scroll '{slug}' was not found.")

# --- APP STARTUP & SHUTDOWN ---
app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    global engine, scout
    if settings.gemini_api_key:
        engine = SagaEngine(gemini_api_key=settings.gemini_api_key, ip_geolocation_api_key=settings.ip_geolocation_api_key)
        scout = MarketplaceScout()
        await connect_to_mongo(settings.mongo_uri)
        logger.info("Saga's Engine, Scout, and Memory Scrolls are awake and ready.")
    else:
        logger.error("GEMINI_API_KEY not found. Saga cannot awaken.")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# --- END OF FILE backend/server.py ---