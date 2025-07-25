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
from pydantic_settings import BaseSettings
from typing import Any, Optional, List, Dict, Literal
from bson import ObjectId

# --- NEW: Import Celery and the Engine ---
from backend.celery_app import celery_app
from celery.result import AsyncResult
from backend.engine import SagaEngine

from backend.database import connect_to_mongo, close_mongo_connection, get_database
import motor.motor_asyncio

logger = logging.getLogger(__name__)

# --- CONFIGURATION SETTINGS ---
class Settings(BaseSettings):
    gemini_api_keys: str = Field(..., alias='GEMINI_API_KEYS')
    mongo_uri: str
    admin_api_key: str = Field(..., alias='ADMIN_API_KEY')
    celery_broker_url: str = Field("redis://localhost:6379/0", alias='CELERY_BROKER_URL')
    celery_result_backend: str = Field("redis://localhost:6379/0", alias='CELERY_RESULT_BACKEND')
    

# --- PYDANTIC MODELS (Refactored for Job-Based Architecture) ---

# Models for dispatching jobs
class JobDispatchResponse(BaseModel):
    task_id: str
    status: str = "PENDING"
    message: str = "The prophecy has been dispatched to the Seers for divination."

# Models for checking job status
class JobStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None

# Models for prophecy requests (remain the same)
class AssetInfo(BaseModel): type: Optional[str] = None; name: Optional[str] = None; description: Optional[str] = None; promo_link: Optional[str] = None
class GrandStrategyRequest(BaseModel): interest: str; sub_niche: Optional[str] = None; user_content_text: Optional[str] = None; user_content_url: Optional[str] = None; target_country_name: Optional[str] = None; asset_info: Optional[AssetInfo] = None
class VentureBrief(BaseModel): business_model: Optional[str] = None; primary_strength: Optional[str] = None; investment_level: Optional[str] = None
class NewVentureRequest(BaseModel): interest: str; sub_niche: Optional[str] = None; user_content_text: Optional[str] = None; user_content_url: Optional[str] = None; target_country_name: Optional[str] = None; venture_brief: Optional[VentureBrief] = None
class MarketingAnglesRequest(BaseModel): product_name: str; product_description: str; target_audience: str; asset_type: Literal["Ad Copy", "Landing Page", "Email Copy", "Funnel Page", "Affiliate Copy"]
class PODOpportunitiesRequest(BaseModel): niche_interest: str; style: str
class CommerceAuditRequest(BaseModel): prophecy_type: Literal["Commerce Audit"] = "Commerce Audit"; audit_type: Literal["Account Audit", "Store Audit", "Account Prediction"]; statement_text: Optional[str] = None; store_url: Optional[str] = None
class ArbitragePathsRequest(BaseModel): prophecy_type: Literal["Arbitrage Paths"] = "Arbitrage Paths"; mode: Literal["User_Buys_User_Sells", "Saga_Buys_User_Sells", "User_Buys_Saga_Sells", "Saga_Buys_Saga_Sells"]; product_name: Optional[str] = None; buy_from_url: Optional[str] = None; sell_on_url: Optional[str] = None; category: Optional[str] = None; subcategory: Optional[str] = None
class SocialSellingSagaRequest(BaseModel): prophecy_type: Literal["Social Selling Saga"] = "Social Selling Saga"; product_name: str; social_selling_price: float; desired_profit_per_product: float; social_platform: str = "Instagram"; ads_daily_budget: float = 10.0; product_category: Optional[str] = None; product_subcategory: Optional[str] = None
class ProductRouteRequest(BaseModel): prophecy_type: Literal["Product Route"] = "Product Route"; location_type: Literal["Global", "My Location"]

# --- BREAKING CHANGE: Models for multi-step prophecies now require full context ---
class NewVentureBlueprintRequest(BaseModel):
    chosen_vision: Dict[str, Any]
    # Context from the first task's result is now passed explicitly
    retrieved_histories: Dict[str, Any]
    user_tone_instruction: str
    country_name: str
class MarketingAssetRequest(BaseModel):
    angle_data: Dict[str, Any]  # The full angle object from the previous task
    platform: Optional[str] = None
    length: Optional[str] = None
class PODPackageRequest(BaseModel):
    opportunity_data: Dict[str, Any] # The full concept object from the previous task

# Grimoire models remain unchanged
class GrimoirePageBase(BaseModel): title: str; slug: str; author: str = "Saga"; content: str; summary: str; tags: List[str] = [];
class GrimoirePageCreate(GrimoirePageBase): pass # ... (rest of grimoire models are the same)
class GrimoirePageUpdate(BaseModel): title: Optional[str] = None; slug: Optional[str] = None; content: Optional[str] = None; summary: Optional[str] = None; tags: Optional[List[str]] = None;
class GrimoirePageDB(GrimoirePageBase): id: str = Field(..., alias="_id"); created_at: datetime = Field(default_factory=datetime.utcnow); class Config: json_encoders = {ObjectId: str}; allow_population_by_field_name = True
class TopicRequest(BaseModel): topic: str
class TitleRequest(BaseModel): title: str; topic: str

# --- FASTAPI APP AND ROUTER ---
app = FastAPI(title="Saga AI", version="13.0.0 (Resilient Architecture)", description="The Oracle of Strategy, now empowered with a resilient, job-based prophecy system.")
api_router = APIRouter(prefix="/api/v10")
engine: SagaEngine = None
settings = Settings()

# --- Security Dependency ---
async def verify_admin_key(x_admin_api_key: str = Header(...)):
    if x_admin_api_key != settings.admin_api_key: raise HTTPException(status_code=401, detail="Unauthorized")

# --- API ENDPOINTS (REFORGED) ---
@api_router.get("/health", tags=["1. System"])
async def health_check(): return {"message": "Saga is conscious and the Bifrost to this API is open."}

# --- NEW: Endpoint to check prophecy status ---
@api_router.get("/prophesy/status/{task_id}", response_model=JobStatusResponse, tags=["2. Prophecy Status"])
async def get_prophecy_status(task_id: str):
    """Checks the status of a dispatched prophecy task."""
    task_result = AsyncResult(task_id, app=celery_app)
    result = None
    if task_result.successful():
        result = task_result.get()
    elif task_result.failed():
        # Capture the error information from the task
        result = {"error": "Prophecy failed", "details": str(task_result.info)}
    
    return JobStatusResponse(task_id=task_id, status=task_result.status, result=result)

# --- REFACTORED: Prophecy endpoints now dispatch jobs ---
@api_router.post("/prophesy/grand-strategy", status_code=202, response_model=JobDispatchResponse, tags=["3. Prophecy Dispatchers"])
async def dispatch_grand_strategy(request: GrandStrategyRequest):
    if not engine: raise HTTPException(status_code=503, detail="Saga is slumbering.")
    task_id = engine.delegate_grand_strategy(**request.model_dump(exclude_unset=True))
    return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/new-venture-visions", status_code=202, response_model=JobDispatchResponse, tags=["3. Prophecy Dispatchers"])
async def dispatch_new_venture_visions(request: NewVentureRequest):
    task_id = engine.delegate_new_venture_visions(**request.model_dump(exclude_unset=True))
    return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/new-venture-blueprint", status_code=202, response_model=JobDispatchResponse, tags=["3. Prophecy Dispatchers"])
async def dispatch_new_venture_blueprint(request: NewVentureBlueprintRequest):
    task_id = engine.delegate_venture_blueprint(**request.model_dump())
    return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/commerce", status_code=202, response_model=JobDispatchResponse, tags=["3. Prophecy Dispatchers"])
async def dispatch_commerce_prophecy(request: CommerceAuditRequest | ArbitragePathsRequest | SocialSellingSagaRequest | ProductRouteRequest):
    task_id = engine.delegate_commerce_saga(**request.model_dump())
    return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/marketing/angles", status_code=202, response_model=JobDispatchResponse, tags=["3. Prophecy Dispatchers"])
async def dispatch_marketing_angles(request: MarketingAnglesRequest):
    task_id = engine.delegate_marketing_angles(**request.model_dump())
    return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/marketing/asset", status_code=202, response_model=JobDispatchResponse, tags=["3. Prophecy Dispatchers"])
async def dispatch_marketing_asset(request: MarketingAssetRequest):
    task_id = engine.delegate_marketing_asset(**request.model_dump(exclude_unset=True))
    return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/pod/opportunities", status_code=202, response_model=JobDispatchResponse, tags=["3. Prophecy Dispatchers"])
async def dispatch_pod_opportunities(request: PODOpportunitiesRequest):
    task_id = engine.delegate_pod_opportunities(**request.model_dump())
    return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/pod/package", status_code=202, response_model=JobDispatchResponse, tags=["3. Prophecy Dispatchers"])
async def dispatch_pod_package(request: PODPackageRequest):
    task_id = engine.delegate_pod_package(**request.model_dump())
    return JobDispatchResponse(task_id=task_id)

# --- Grimoire endpoints remain synchronous and unchanged for admin simplicity ---
@api_router.post("/grimoire/inscribe", status_code=201, response_model=GrimoirePageDB, tags=["4. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def create_grimoire_page(page: GrimoirePageCreate, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    page_dict = page.model_dump(); page_dict["created_at"] = datetime.utcnow()
    # ... (logic remains the same)
    if await db.grimoire_pages.find_one({"slug": page_dict["slug"]}): raise HTTPException(status_code=400, detail="A scroll with this slug already exists.")
    result = await db.grimoire_pages.insert_one(page_dict)
    created_page = await db.grimoire_pages.find_one({"_id": result.inserted_id}); return GrimoirePageDB.model_validate(created_page)

# ... (All other Grimoire endpoints: GET all, GET one, PUT, DELETE, generate-titles, generate-content remain unchanged)
@api_router.get("/grimoire/scrolls", response_model=List[GrimoirePageDB], tags=["4. Saga Grimoire"])
async def get_all_grimoire_pages(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    pages_cursor = db.grimoire_pages.find().sort("created_at", -1); pages = await pages_cursor.to_list(length=100); return [GrimoirePageDB.model_validate(page) for page in pages]
@api_router.get("/grimoire/scrolls/{slug}", response_model=GrimoirePageDB, tags=["4. Saga Grimoire"])
async def get_grimoire_page_by_slug(slug: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    page = await db.grimoire_pages.find_one({"slug": slug});
    if page: return GrimoirePageDB.model_validate(page)
    raise HTTPException(status_code=404, detail=f"The scroll '{slug}' was not found.")
@api_router.put("/grimoire/scrolls/{id}", response_model=GrimoirePageDB, tags=["4. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def update_grimoire_page(id: str, page_update: GrimoirePageUpdate, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    update_data = page_update.model_dump(exclude_unset=True) # ... logic remains ...
    if not update_data: raise HTTPException(status_code=400, detail="No update data provided.")
    if "slug" in update_data and await db.grimoire_pages.find_one({"slug": update_data["slug"], "_id": {"$ne": ObjectId(id)}}): raise HTTPException(status_code=400, detail="Another scroll with this slug already exists.")
    await db.grimoire_pages.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    updated_page = await db.grimoire_pages.find_one({"_id": ObjectId(id)})
    if updated_page: return GrimoirePageDB.model_validate(updated_page)
    raise HTTPException(status_code=404, detail=f"The scroll with id '{id}' could not be updated.")
@api_router.delete("/grimoire/scrolls/{id}", status_code=204, tags=["4. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def delete_grimoire_page(id: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    delete_result = await db.grimoire_pages.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 0: raise HTTPException(status_code=404, detail=f"The scroll with id '{id}' was not found.")
# AI helpers for Grimoire also remain sync
@api_router.post("/grimoire/generate-titles", tags=["4. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def generate_grimoire_titles(request: TopicRequest):
    return await engine.content_saga_stack.prophesy_title_slug_concepts(request.topic)
@api_router.post("/grimoire/generate-content", tags=["4. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def generate_grimoire_content(request: TitleRequest):
    return await engine.content_saga_stack.prophesy_full_scroll_content(request.title, request.topic)


# --- APP STARTUP & SHUTDOWN ---
app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    global engine
    load_dotenv()
    engine = SagaEngine() # Initialize the Singleton engine
    await connect_to_mongo(settings.mongo_uri)
    logger.info("Saga's Engine and Memory Scrolls are awake and ready.")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
# --- END OF FILE backend/server.py ---