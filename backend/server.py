# --- START OF FILE backend/server.py ---
import os
import logging
from pathlib import Path
import uuid
from datetime import datetime, timezone
import re

from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional, List, Dict, Literal
from bson import ObjectId

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
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- PYDANTIC MODELS ---

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    class Config: allow_population_by_field_name = True

class ProphecyHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    session_id: str
    task_id: str
    stack: str
    status: str = "PENDING"
    prophecy_data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    class Config: allow_population_by_field_name = True

class JobDispatchResponse(BaseModel): task_id: str; status: str = "PENDING"
class JobStatusResponse(BaseModel): task_id: str; status: str; result: Optional[Any] = None

# --- Request Models ---
class BaseProphecyRequest(BaseModel): session_id: str
class GrandStrategyRequest(BaseProphecyRequest): interest: str; sub_niche: Optional[str] = None; user_content_text: Optional[str] = None; user_content_url: Optional[str] = None; target_country_name: Optional[str] = None; asset_info: Optional[Dict] = None
class VentureBrief(BaseModel): business_model: Optional[str] = None; primary_strength: Optional[str] = None; investment_level: Optional[str] = None
class NewVentureRequest(BaseProphecyRequest): interest: str; sub_niche: Optional[str] = None; user_content_text: Optional[str] = None; user_content_url: Optional[str] = None; target_country_name: Optional[str] = None; venture_brief: Optional[VentureBrief] = None
class NewVentureBlueprintRequest(BaseProphecyRequest): chosen_vision: Dict[str, Any]; retrieved_histories: Dict[str, Any]; user_tone_instruction: str; country_name: str
class MarketingAnglesRequest(BaseProphecyRequest): product_name: str; product_description: str; target_audience: str; asset_type: str
class MarketingAssetRequest(BaseProphecyRequest): angle_data: Dict[str, Any]; platform: Optional[str] = None; length: Optional[str] = None
class PODOpportunitiesRequest(BaseProphecyRequest): niche_interest: str; style: str
class PODPackageRequest(BaseProphecyRequest): opportunity_data: Dict[str, Any]
class CommerceRequest(BaseProphecyRequest): prophecy_type: str; audit_type: Optional[str] = None; mode: Optional[str] = None; statement_text: Optional[str] = None; store_url: Optional[str] = None; product_name: Optional[str] = None; buy_from_url: Optional[str] = None; sell_on_url: Optional[str] = None; social_selling_price: Optional[float] = None; desired_profit_per_product: Optional[float] = None; social_platform: Optional[str] = None; ads_daily_budget: Optional[float] = None; location_type: Optional[str] = None
class ContentSagaRequest(BaseProphecyRequest): content_type: str; tactical_interest: Optional[str] = None; retrieved_histories: Optional[Dict] = None; spark: Optional[Dict] = None; platform: Optional[str] = None; length: Optional[str] = None; post_to_comment_on: Optional[str] = None

# Grimoire Models
class GrimoirePageBase(BaseModel):
    title: str
    slug: str
    author: str = "Saga"
    content: str
    summary: str
    tags: List[str] = []

    @validator('slug', pre=True, always=True)
    def generate_slug_from_title(cls, v, values):
        if not v or v.strip() == "":
            title = values.get('title', '')
            s = title.lower().strip()
            s = re.sub(r'[\s\W-]+', '-', s)
            return s.strip('-')
        return v

class GrimoirePageCreate(GrimoirePageBase): pass
class GrimoirePageUpdate(BaseModel): title: Optional[str] = None; slug: Optional[str] = None; content: Optional[str] = None; summary: Optional[str] = None; tags: Optional[List[str]] = None
class GrimoirePageDB(GrimoirePageBase): id: str = Field(..., alias="_id"); created_at: datetime = Field(default_factory=datetime.utcnow); class Config: json_encoders = {ObjectId: str}; allow_population_by_field_name = True
class TopicRequest(BaseModel): topic: str
class TitleRequest(BaseModel): title: str; topic: str

# --- FASTAPI APP, ROUTER, AND GLOBALS ---
app = FastAPI(title="Saga AI", version="13.1.0 (Persistent Memory)", description="The Oracle of Strategy, now with persistent, anonymous user sessions.")
api_router = APIRouter(prefix="/api/v10")
engine: SagaEngine = None
settings = Settings()

# --- Security ---
async def verify_admin_key(x_admin_api_key: str = Header(...)):
    if x_admin_api_key != settings.admin_api_key: raise HTTPException(status_code=401, detail="Unauthorized")

# --- Helper to create prophecy history record ---
async def create_history(session_id: str, task_id: str, stack: str, db: motor.motor_asyncio.AsyncIOMotorDatabase):
    history_record = ProphecyHistory(session_id=session_id, task_id=task_id, stack=stack)
    await db.prophecy_history.insert_one(history_record.model_dump(by_alias=True))

# --- API ENDPOINTS ---
@api_router.get("/health", tags=["1. System"])
async def health_check(): return {"message": "Saga is conscious."}

@api_router.post("/session/create", response_model=Session, tags=["2. Session Management"])
async def create_session(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    session = Session(); await db.sessions.insert_one(session.model_dump(by_alias=True)); return session

@api_router.get("/prophesy/status/{task_id}", response_model=JobStatusResponse, tags=["3. Prophecy Status"])
async def get_prophecy_status(task_id: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_result = AsyncResult(task_id, app=celery_app); result = None
    if task_result.ready():
        update = {"updated_at": datetime.now(timezone.utc)}
        if task_result.successful():
            result = task_result.get(); update["status"] = "SUCCESS"; update["prophecy_data"] = result
        else:
            result = {"error": "Prophecy failed", "details": str(task_result.info)}; update["status"] = "FAILURE"; update["prophecy_data"] = result
        await db.prophecy_history.update_one({"task_id": task_id}, {"$set": update})
    return JobStatusResponse(task_id=task_id, status=task_result.status, result=result)

@api_router.post("/prophesy/grand-strategy", status_code=202, response_model=JobDispatchResponse, tags=["4. Prophecy Dispatchers"])
async def dispatch_grand_strategy(req: GrandStrategyRequest, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_id = engine.delegate_grand_strategy(**req.model_dump()); await create_history(req.session_id, task_id, "Grand Strategy", db); return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/new-venture-visions", status_code=202, response_model=JobDispatchResponse, tags=["4. Prophecy Dispatchers"])
async def dispatch_new_venture_visions(req: NewVentureRequest, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_id = engine.delegate_new_venture_visions(**req.model_dump()); await create_history(req.session_id, task_id, "New Venture Visions", db); return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/new-venture-blueprint", status_code=202, response_model=JobDispatchResponse, tags=["4. Prophecy Dispatchers"])
async def dispatch_new_venture_blueprint(req: NewVentureBlueprintRequest, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_id = engine.delegate_venture_blueprint(**req.model_dump()); await create_history(req.session_id, task_id, "New Venture Blueprint", db); return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/marketing/angles", status_code=202, response_model=JobDispatchResponse, tags=["4. Prophecy Dispatchers"])
async def dispatch_marketing_angles(req: MarketingAnglesRequest, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_id = engine.delegate_marketing_angles(**req.model_dump()); await create_history(req.session_id, task_id, "Marketing Angles", db); return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/marketing/asset", status_code=202, response_model=JobDispatchResponse, tags=["4. Prophecy Dispatchers"])
async def dispatch_marketing_asset(req: MarketingAssetRequest, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_id = engine.delegate_marketing_asset(**req.model_dump()); await create_history(req.session_id, task_id, "Marketing Asset", db); return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/pod/opportunities", status_code=202, response_model=JobDispatchResponse, tags=["4. Prophecy Dispatchers"])
async def dispatch_pod_opportunities(req: PODOpportunitiesRequest, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_id = engine.delegate_pod_opportunities(**req.model_dump()); await create_history(req.session_id, task_id, "POD Opportunities", db); return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/pod/package", status_code=202, response_model=JobDispatchResponse, tags=["4. Prophecy Dispatchers"])
async def dispatch_pod_package(req: PODPackageRequest, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_id = engine.delegate_pod_package(**req.model_dump()); await create_history(req.session_id, task_id, "POD Package", db); return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/commerce", status_code=202, response_model=JobDispatchResponse, tags=["4. Prophecy Dispatchers"])
async def dispatch_commerce_saga(req: CommerceRequest, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_id = engine.delegate_commerce_saga(**req.model_dump()); await create_history(req.session_id, task_id, f"Commerce: {req.prophecy_type}", db); return JobDispatchResponse(task_id=task_id)

@api_router.post("/prophesy/content-saga", status_code=202, response_model=JobDispatchResponse, tags=["4. Prophecy Dispatchers"])
async def dispatch_content_saga(req: ContentSagaRequest, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    task_id = engine.delegate_content_saga_task(**req.model_dump()); await create_history(req.session_id, task_id, f"Content: {req.content_type}", db); return JobDispatchResponse(task_id=task_id)

# --- Grimoire Admin Endpoints ---
@api_router.post("/grimoire/inscribe", status_code=201, response_model=GrimoirePageDB, tags=["5. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def create_grimoire_page(page: GrimoirePageCreate, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    page_dict = page.model_dump(); page_dict["created_at"] = datetime.now(timezone.utc)
    if await db.grimoire_pages.find_one({"slug": page_dict["slug"]}): raise HTTPException(status_code=400, detail="Slug already exists.")
    result = await db.grimoire_pages.insert_one(page_dict); new_page = await db.grimoire_pages.find_one({"_id": result.inserted_id}); return GrimoirePageDB.model_validate(new_page)

@api_router.get("/grimoire/scrolls", response_model=List[GrimoirePageDB], tags=["5. Saga Grimoire"])
async def get_all_grimoire_pages(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    cursor = db.grimoire_pages.find().sort("created_at", -1); pages = await cursor.to_list(length=100); return [GrimoirePageDB.model_validate(page) for page in pages]

@api_router.get("/grimoire/scrolls/{slug}", response_model=GrimoirePageDB, tags=["5. Saga Grimoire"])
async def get_grimoire_page_by_slug(slug: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    page = await db.grimoire_pages.find_one({"slug": slug});
    if page: return GrimoirePageDB.model_validate(page)
    raise HTTPException(status_code=404, detail="Scroll not found.")

@api_router.put("/grimoire/scrolls/{id}", response_model=GrimoirePageDB, tags=["5. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def update_grimoire_page(id: str, page_update: GrimoirePageUpdate, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    update_data = page_update.model_dump(exclude_unset=True)
    if not update_data: raise HTTPException(status_code=400, detail="No update data provided.")
    if "slug" in update_data:
        existing = await db.grimoire_pages.find_one({"slug": update_data["slug"], "_id": {"$ne": ObjectId(id)}})
        if existing: raise HTTPException(status_code=400, detail="Slug already in use.")
    await db.grimoire_pages.update_one({"_id": ObjectId(id)}, {"$set": update_data}); updated_page = await db.grimoire_pages.find_one({"_id": ObjectId(id)})
    if updated_page: return GrimoirePageDB.model_validate(updated_page)
    raise HTTPException(status_code=404, detail="Could not update scroll.")

@api_router.delete("/grimoire/scrolls/{id}", status_code=204, tags=["5. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def delete_grimoire_page(id: str, db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)):
    res = await db.grimoire_pages.delete_one({"_id": ObjectId(id)});
    if res.deleted_count == 0: raise HTTPException(status_code=404, detail="Scroll not found.")

@api_router.post("/grimoire/generate-titles", tags=["5. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def generate_grimoire_titles(request: TopicRequest):
    return await engine.content_saga_stack.prophesy_title_slug_concepts(request.topic)

# FIX: Corrected typo from `api_outer.post` to `api_router.post`
@api_router.post("/grimoire/generate-content", tags=["5. Saga Grimoire"], dependencies=[Depends(verify_admin_key)])
async def generate_grimoire_content(request: TitleRequest):
    return await engine.content_saga_stack.prophesy_full_scroll_content(request.title, request.topic)

# --- APP LIFECYCLE ---
@app.on_event("startup")
async def startup_event():
    global engine, settings; load_dotenv(); settings = Settings(); engine = SagaEngine(); await connect_to_mongo(settings.mongo_uri)
    logger.info("Saga's Engine and Memory Scrolls are awake and ready.")

@app.on_event("shutdown")
async def shutdown_event(): await close_mongo_connection()

app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
# --- END OF FILE backend/server.py ---