from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import asyncio
from supabase import create_client, Client
from emergentintegrations.llm.chat import LlmChat, UserMessage
from pytrends.request import TrendReq
import random
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize Supabase client
supabase: Client = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
)

# MongoDB connection (fallback for some operations)
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Oracle Engine", description="AI-Powered Trend Prediction & Content Generation")
api_router = APIRouter(prefix="/api")

# --- MODELS ---
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
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        
    async def monitor_niche_trends(self, niche: str, keywords: List[str] = None) -> List[TrendData]:
        """Monitor trends for a specific niche using Google Trends and simulated data"""
        trends = []
        
        try:
            # Initialize pytrends
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Base keywords for the niche
            if not keywords:
                keywords = [niche]
            
            # Expand keywords based on niche
            expanded_keywords = self._expand_niche_keywords(niche, keywords)
            
            # Get trends for each keyword set (max 5 at a time for Google Trends)
            for i in range(0, len(expanded_keywords), 5):
                keyword_batch = expanded_keywords[i:i+5]
                
                try:
                    pytrends.build_payload(keyword_batch, cat=0, timeframe='now 1-d', geo='', gprop='')
                    interest_data = pytrends.interest_over_time()
                    
                    if not interest_data.empty:
                        for keyword in keyword_batch:
                            if keyword in interest_data.columns:
                                latest_values = interest_data[keyword].tail(3).tolist()
                                avg_score = sum(latest_values) / len(latest_values) if latest_values else 0
                                
                                # Calculate velocity (trend acceleration)
                                velocity = self._calculate_velocity(latest_values)
                                
                                trends.append(TrendData(
                                    niche=niche,
                                    title=f"Trending: {keyword}",
                                    content=f"Search interest for '{keyword}' showing momentum in the {niche} space",
                                    source="Google Trends",
                                    trend_score=avg_score / 100.0,
                                    velocity=velocity
                                ))
                except Exception as e:
                    logging.warning(f"Error fetching trends for {keyword_batch}: {e}")
                
                # Add delay to respect rate limits
                await asyncio.sleep(1)
                
        except Exception as e:
            logging.error(f"Error in trend monitoring: {e}")
        
        # Add some simulated high-value trends for demo
        simulated_trends = self._generate_simulated_trends(niche)
        trends.extend(simulated_trends)
        
        # Sort by trend score and velocity
        trends.sort(key=lambda x: x.trend_score * x.velocity, reverse=True)
        
        return trends[:10]  # Return top 10 trends
    
    def _expand_niche_keywords(self, niche: str, base_keywords: List[str]) -> List[str]:
        """Expand keywords based on niche"""
        niche_expansions = {
            'fitness': ['workout', 'nutrition', 'supplements', 'training', 'wellness'],
            'crypto': ['bitcoin', 'ethereum', 'defi', 'nft', 'blockchain'],
            'saas': ['software', 'automation', 'productivity', 'business tools', 'cloud'],
            'ecommerce': ['dropshipping', 'shopify', 'amazon fba', 'online store', 'marketplace'],
            'real estate': ['property investment', 'rental income', 'house flipping', 'commercial real estate'],
            'marketing': ['digital marketing', 'social media', 'seo', 'advertising', 'content marketing']
        }
        
        expanded = base_keywords.copy()
        if niche.lower() in niche_expansions:
            expanded.extend(niche_expansions[niche.lower()])
        
        return list(set(expanded))  # Remove duplicates
    
    def _calculate_velocity(self, values: List[float]) -> float:
        """Calculate trend velocity (acceleration)"""
        if len(values) < 2:
            return 0.0
        
        # Simple velocity calculation: recent change rate
        recent_change = values[-1] - values[0] if len(values) >= 2 else 0
        return max(0, recent_change / 100.0)  # Normalize to 0-1
    
    def _generate_simulated_trends(self, niche: str) -> List[TrendData]:
        """Generate simulated high-value trends for demonstration"""
        niche_trends = {
            'fitness': [
                "AI-powered fitness tracking wearables",
                "Plant-based protein alternatives gaining momentum",
                "Cold plunge therapy for recovery",
                "Functional fitness movements"
            ],
            'crypto': [
                "Layer 2 scaling solutions adoption",
                "Institutional Bitcoin accumulation",
                "DeFi yield farming strategies",
                "NFT utility in gaming"
            ],
            'saas': [
                "AI workflow automation tools",
                "No-code development platforms",
                "Customer success automation",
                "API-first architecture"
            ]
        }
        
        default_trends = [
            f"Emerging {niche} market opportunities",
            f"Innovation in {niche} technology",
            f"{niche} consumer behavior shifts"
        ]
        
        trends_list = niche_trends.get(niche.lower(), default_trends)
        simulated = []
        
        for i, trend in enumerate(trends_list[:4]):  # Limit to 4 simulated trends
            simulated.append(TrendData(
                niche=niche,
                title=trend,
                content=f"High-velocity trend detected in {niche} space: {trend}. Analysis shows significant growth potential.",
                source="Oracle Intelligence",
                trend_score=random.uniform(0.6, 0.95),
                velocity=random.uniform(0.4, 0.8)
            ))
        
        return simulated
    
    async def generate_content(self, niche: str, trends: List[str], content_type: str) -> GeneratedContent:
        """Generate AI-powered content based on trends"""
        
        # Choose AI model based on content type
        if content_type == 'ad_copy':
            # Use OpenAI for ad copy (better for persuasive writing)
            api_key = self.openai_key
            model_provider = "openai"
            model_name = "gpt-4o"
            system_prompt = """You are an expert direct-response copywriter specializing in high-converting ad copy. 
            Create compelling, action-driven advertisements that follow proven frameworks like AIDA, PAS, and SCAB.
            Focus on benefits, urgency, and clear calls-to-action."""
        else:
            # Use Gemini for social posts and affiliate content
            api_key = self.gemini_key
            model_provider = "gemini"
            model_name = "gemini-2.5-flash-preview-04-17"
            system_prompt = """You are a social media expert and content strategist. 
            Create engaging, shareable content that resonates with target audiences and drives engagement.
            Focus on storytelling, value delivery, and authentic connection."""
        
        # Create content prompt based on type
        trend_context = "\n".join([f"- {trend}" for trend in trends])
        
        prompts = {
            'ad_copy': f"""Create high-converting ad copy for the {niche} niche based on these trending topics:
{trend_context}

Requirements:
- Write 3 different ad variations (short, medium, long)
- Include compelling headlines with urgency
- Use proven copywriting frameworks
- Include clear call-to-action
- Focus on benefits and transformation
- Target audience pain points and desires

Format as: **Headline** | Body Copy | **CTA**""",

            'social_post': f"""Create engaging social media content for the {niche} niche based on these trends:
{trend_context}

Requirements:
- Create 3 platform-specific posts (Twitter/X, LinkedIn, Instagram)
- Include relevant hashtags
- Engaging hooks and value-driven content
- Encourage interaction and sharing
- Maintain authentic tone
- Include content pillars: education, inspiration, entertainment

Format each post with platform label and content.""",

            'affiliate_review': f"""Create persuasive affiliate marketing content for the {niche} niche based on these trends:
{trend_context}

Requirements:
- Write product review outline with pros/cons
- Include personal experience narrative
- Address common objections
- Highlight key benefits and unique selling points
- Include comparison with alternatives
- Clear recommendation and affiliate disclosure

Format as structured review with sections."""
        }
        
        try:
            # Initialize LLM chat
            chat = LlmChat(
                api_key=api_key,
                session_id=f"{content_type}-{uuid.uuid4()}",
                system_message=system_prompt
            ).with_model(model_provider, model_name).with_max_tokens(4096)
            
            # Generate content
            user_message = UserMessage(text=prompts[content_type])
            response = await chat.send_message(user_message)
            
            # Calculate confidence score based on response length and quality indicators
            confidence = min(0.95, 0.7 + (len(response) / 2000) * 0.25)
            
            return GeneratedContent(
                niche=niche,
                content_type=content_type,
                title=f"{content_type.replace('_', ' ').title()} for {niche}",
                content=response,
                confidence_score=confidence
            )
            
        except Exception as e:
            logging.error(f"Error generating content: {e}")
            raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

# Initialize Oracle Engine
oracle = OracleEngine()

# --- API ENDPOINTS ---

@api_router.get("/")
async def root():
    return {"message": "Oracle Engine - AI-Powered Trend Prediction & Content Generation"}

@api_router.post("/niche/analyze", response_model=TrendAnalysis)
async def analyze_niche(request: NicheRequest):
    """Analyze trends for a specific niche"""
    try:
        # Get trend data
        trends = await oracle.monitor_niche_trends(request.niche, request.keywords)
        
        # Store trends in Supabase
        for trend in trends:
            trend_dict = trend.dict()
            trend_dict['created_at'] = trend_dict['created_at'].isoformat()
            supabase.table('trends').insert(trend_dict).execute()
        
        # Generate forecast summary
        top_trends = [trend.title for trend in trends[:5]]
        forecast_prompt = f"Based on these top trends in {request.niche}: {', '.join(top_trends)}, provide a brief forecast summary and top 3 opportunities."
        
        # Use Gemini for analysis
        chat = LlmChat(
            api_key=oracle.gemini_key,
            session_id=f"forecast-{uuid.uuid4()}",
            system_message="You are a trend analyst providing concise, actionable insights."
        ).with_model("gemini", "gemini-2.5-flash-preview-04-17")
        
        forecast_response = await chat.send_message(UserMessage(text=forecast_prompt))
        
        # Extract opportunities (simplified)
        opportunities = [
            f"Capitalize on {trends[0].title if trends else 'emerging trends'}",
            f"Create content around {request.niche} innovation",
            f"Target early adopters in {request.niche} space"
        ]
        
        analysis = TrendAnalysis(
            niche=request.niche,
            trends=trends,
            forecast_summary=forecast_response[:500] + "..." if len(forecast_response) > 500 else forecast_response,
            top_opportunities=opportunities
        )
        
        return analysis
        
    except Exception as e:
        logging.error(f"Error analyzing niche: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/content/generate", response_model=GeneratedContent)
async def generate_content(request: ForecastRequest):
    """Generate AI-powered marketing content"""
    try:
        content = await oracle.generate_content(
            request.niche, 
            request.trend_data, 
            request.content_type
        )
        
        # Store in Supabase
        content_dict = content.dict()
        content_dict['created_at'] = content_dict['created_at'].isoformat()
        supabase.table('generated_content').insert(content_dict).execute()
        
        return content
        
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/content/history/{niche}")
async def get_content_history(niche: str):
    """Get content generation history for a niche"""
    try:
        response = supabase.table('generated_content').select("*").eq('niche', niche).order('created_at', desc=True).limit(20).execute()
        return {"content_history": response.data}
    except Exception as e:
        logging.error(f"Error fetching content history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trends/latest/{niche}")
async def get_latest_trends(niche: str):
    """Get latest trends for a niche"""
    try:
        response = supabase.table('trends').select("*").eq('niche', niche).order('created_at', desc=True).limit(10).execute()
        return {"trends": response.data}
    except Exception as e:
        logging.error(f"Error fetching trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get counts from Supabase
        trends_count = supabase.table('trends').select("id", count="exact").execute()
        content_count = supabase.table('generated_content').select("id", count="exact").execute()
        
        return {
            "total_trends_monitored": trends_count.count or 0,
            "content_pieces_generated": content_count.count or 0,
            "active_niches": ["fitness", "crypto", "saas", "ecommerce", "marketing"],
            "system_status": "operational"
        }
    except Exception as e:
        logging.error(f"Error fetching stats: {e}")
        return {
            "total_trends_monitored": 0,
            "content_pieces_generated": 0,
            "active_niches": [],
            "system_status": "degraded"
        }

# Include router in main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    try:
        # Create tables if they don't exist
        # Note: In production, you'd run migrations separately
        logger.info("Oracle Engine startup complete")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()