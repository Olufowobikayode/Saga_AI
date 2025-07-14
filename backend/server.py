from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
import asyncio
import google.generativeai as genai
from pytrends.request import TrendReq
import random

# --- INITIAL SETUP ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- DATABASE AND API CLIENTS ---
# This block will now safely initialize clients or fail with a clear error
# if environment variables are missing on Render.
try:
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    gemini_api_key = os.environ['GEMINI_API_KEY']

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    genai.configure(api_key=gemini_api_key)

except KeyError as e:
    logger.error(f"FATAL: Environment variable {e} not set. The application cannot start.")
    raise

# --- Pydantic MODELS ---
class NicheRequest(BaseModel):
    niche: str
    keywords: List[str] = []

class TrendData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    niche: str
    title: str
    content: str
    source: str
    trend_score: float
    velocity: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ForecastRequest(BaseModel):
    niche: str
    trend_data: List[str]
    content_type: str  # 'ad_copy', 'social_post', 'affiliate_review'

class GeneratedContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    niche: str
    content_type: str
    title: str
    content: str
    confidence_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TrendAnalysis(BaseModel):
    niche: str
    trends: List[TrendData]
    forecast_summary: str
    top_opportunities: List[str]

# --- ORACLE ENGINE CORE ---
class OracleEngine:
    def __init__(self):
        # Initialize the Gemini model once for reuse across the application.
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    async def monitor_niche_trends(self, niche: str, keywords: List[str] = None) -> List[TrendData]:
        trends = []
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            if not keywords:
                keywords = [niche]
            
            expanded_keywords = self._expand_niche_keywords(niche, keywords)
            
            for i in range(0, min(len(expanded_keywords), 10), 5):
                keyword_batch = expanded_keywords[i:i+5]
                try:
                    # Using asyncio.to_thread to run the synchronous pytrends library in a non-blocking way
                    interest_data = await asyncio.to_thread(pytrends.build_payload, keyword_batch, cat=0, timeframe='now 1-d', geo='', gprop='')
                    interest_data = pytrends.interest_over_time()
                    
                    if not interest_data.empty:
                        for keyword in keyword_batch:
                            if keyword in interest_data.columns:
                                latest_values = interest_data[keyword].tail(3).tolist()
                                avg_score = sum(latest_values) / len(latest_values) if latest_values else 0
                                velocity = self._calculate_velocity(latest_values)
                                trends.append(TrendData(
                                    niche=niche,
                                    title=f"Trending: {keyword}",
                                    content=f"Search interest for '{keyword}' showing momentum in the {niche} space.",
                                    source="Google Trends",
                                    trend_score=avg_score / 100.0,
                                    velocity=velocity
                                ))
                except Exception as e:
                    logging.warning(f"Error fetching Google Trends for {keyword_batch}: {e}")
                await asyncio.sleep(1) # Respect rate limits
        except Exception as e:
            logging.error(f"Error in trend monitoring: {e}")
        
        simulated_trends = self._generate_simulated_trends(niche)
        trends.extend(simulated_trends)
        trends.sort(key=lambda x: (x.trend_score * x.velocity), reverse=True)
        return trends[:10]

    def _expand_niche_keywords(self, niche: str, base_keywords: List[str]) -> List[str]:
        niche_expansions = {
            'fitness': ['workout', 'nutrition', 'supplements', 'training', 'wellness', 'exercise', 'protein', 'cardio'],
            'crypto': ['bitcoin', 'ethereum', 'defi', 'nft', 'blockchain', 'trading', 'altcoins', 'web3'],
            'saas': ['software', 'automation', 'productivity', 'business tools', 'cloud', 'api', 'integration'],
        }
        expanded = base_keywords.copy()
        if niche.lower() in niche_expansions:
            expanded.extend(niche_expansions[niche.lower()])
        return list(set(expanded))

    def _calculate_velocity(self, values: List[float]) -> float:
        if len(values) < 2: return 0.0
        recent_change = values[-1] - values[0]
        return max(0, min(1.0, recent_change / 100.0))

    def _generate_simulated_trends(self, niche: str) -> List[TrendData]:
        niche_trends = {
            'fitness': ["AI-powered fitness tracking", "Plant-based protein alternatives", "Cold plunge therapy"],
            'crypto': ["Layer 2 scaling solutions", "Institutional Bitcoin accumulation", "DeFi yield farming"],
            'saas': ["AI workflow automation tools", "No-code development platforms", "Customer success automation"]
        }
        trends_list = niche_trends.get(niche.lower(), [f"Emerging {niche} opportunities"])
        return [
            TrendData(
                niche=niche, title=trend, content=f"High-velocity trend: {trend}",
                source="Oracle Intelligence", trend_score=random.uniform(0.7, 0.95), velocity=random.uniform(0.5, 0.85)
            ) for trend in trends_list
        ]

    async def generate_content(self, niche: str, trends: List[str], content_type: str) -> GeneratedContent:
        """Generates AI-powered content using the official Google Gemini SDK."""
        system_prompts = {
            'ad_copy': "You are an expert direct-response copywriter specializing in high-converting ad copy...",
            'social_post': "You are a social media expert and viral content strategist...",
            'affiliate_review': "You are a trusted product reviewer and affiliate marketer..."
        }
        trend_context = "\n".join(f"- {trend}" for trend in trends)
        full_prompt = f"{system_prompts[content_type]}\n\nCreate content for the '{niche}' niche based on these trends:\n{trend_context}"

        try:
            response = await self.model.generate_content_async(full_prompt)
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            confidence = min(0.95, 0.75 + (len(response.text) / 2000) * 0.2)
            
            return GeneratedContent(
                niche=niche, content_type=content_type,
                title=f"{content_type.replace('_', ' ').title()} for {niche}",
                content=response.text, confidence_score=confidence
            )
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            raise HTTPException(status_code=500, detail="Content generation failed.")

# --- FASTAPI APP AND ROUTER ---
app = FastAPI(title="Oracle Engine", description="AI-Powered Trend Prediction & Content Generation")
api_router = APIRouter(prefix="/api")
oracle = OracleEngine()

@api_router.get("/")
async def root():
    return {"message": "Oracle Engine - AI-Powered Trend Prediction & Content Generation"}

@api_router.post("/niche/analyze", response_model=TrendAnalysis)
async def analyze_niche(request: NicheRequest):
    try:
        trends = await oracle.monitor_niche_trends(request.niche, request.keywords)
        if trends:
            await db.trends.insert_many([trend.dict() for trend in trends])

        top_trends_titles = [trend.title for trend in trends[:5]]
        forecast_prompt = f"""Based on these top trends in {request.niche}: {', '.join(top_trends_titles)}, provide a brief, actionable forecast summary (2-3 sentences) and identify the top 3 business opportunities."""
        
        forecast_summary = f"Strong momentum detected in {request.niche}."
        try:
            forecast_response = await oracle.model.generate_content_async(forecast_prompt)
            forecast_summary = forecast_response.text
        except Exception as e:
            logging.warning(f"Forecast generation failed: {e}")

        opportunities = [f"Capitalize on {trends[0].title}" if trends else f"Explore emerging {request.niche} trends", f"Create content for {request.niche} innovators"]
        
        return TrendAnalysis(niche=request.niche, trends=trends, forecast_summary=forecast_summary, top_opportunities=opportunities)
    except Exception as e:
        logger.error(f"Error in analyze_niche: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/content/generate", response_model=GeneratedContent)
async def generate_content_endpoint(request: ForecastRequest):
    try:
        content = await oracle.generate_content(request.niche, request.trend_data, request.content_type)
        await db.generated_content.insert_one(content.dict())
        return content
    except Exception as e:
        logger.error(f"Error in generate_content_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/content/history/{niche}")
async def get_content_history(niche: str):
    cursor = db.generated_content.find({"niche": niche}).sort("created_at", -1).limit(20)
    content_history = [doc for doc in await cursor.to_list(length=20)]
    for doc in content_history:
        doc['_id'] = str(doc['_id'])
    return {"content_history": content_history}

@api_router.get("/trends/latest/{niche}")
async def get_latest_trends(niche: str):
    cursor = db.trends.find({"niche": niche}).sort("created_at", -1).limit(10)
    trends = [doc for doc in await cursor.to_list(length=10)]
    for doc in trends:
        doc['_id'] = str(doc['_id'])
    return {"trends": trends}

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    try:
        trends_count = await db.trends.count_documents({})
        content_count = await db.generated_content.count_documents({})
        distinct_niches = await db.trends.distinct("niche")
        
        return {
            "total_trends_monitored": trends_count,
            "content_pieces_generated": content_count,
            "active_niches": distinct_niches or ["fitness", "crypto", "saas"],
            "system_status": "operational"
        }
    except Exception as e:
        logging.error(f"Error fetching stats: {e}")
        return { "total_trends_monitored": 0, "content_pieces_generated": 0, "active_niches": [], "system_status": "degraded" }

# --- APP CONFIGURATION ---
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        await db.trends.create_index("niche")
        await db.generated_content.create_index("niche")
        logger.info("Oracle Engine startup complete - MongoDB initialized.")
    except Exception as e:
        logger.error(f"Startup error during index creation: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("MongoDB connection closed.")