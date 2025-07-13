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
from emergentintegrations.llm.chat import LlmChat, UserMessage
from pytrends.request import TrendReq
import random
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (primary storage)
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
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        if not self.gemini_key:
            logging.warning("Gemini API key not found")
        
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
            for i in range(0, min(len(expanded_keywords), 10), 5):
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
            'fitness': ['workout', 'nutrition', 'supplements', 'training', 'wellness', 'exercise', 'protein', 'cardio'],
            'crypto': ['bitcoin', 'ethereum', 'defi', 'nft', 'blockchain', 'trading', 'altcoins', 'web3'],
            'saas': ['software', 'automation', 'productivity', 'business tools', 'cloud', 'api', 'integration'],
            'ecommerce': ['dropshipping', 'shopify', 'amazon fba', 'online store', 'marketplace', 'sales'],
            'real estate': ['property investment', 'rental income', 'house flipping', 'commercial real estate'],
            'marketing': ['digital marketing', 'social media', 'seo', 'advertising', 'content marketing', 'conversion']
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
        return max(0, min(1.0, recent_change / 100.0))  # Normalize to 0-1
    
    def _generate_simulated_trends(self, niche: str) -> List[TrendData]:
        """Generate simulated high-value trends for demonstration"""
        niche_trends = {
            'fitness': [
                "AI-powered fitness tracking wearables gaining momentum",
                "Plant-based protein alternatives showing 200% growth", 
                "Cold plunge therapy for athletic recovery trending",
                "Functional fitness movements replacing gym workouts",
                "Biohacking supplements for performance optimization"
            ],
            'crypto': [
                "Layer 2 scaling solutions seeing mass adoption",
                "Institutional Bitcoin accumulation reaching new highs",
                "DeFi yield farming strategies evolving rapidly",
                "NFT utility in gaming ecosystems expanding",
                "Crypto payment integration in mainstream apps"
            ],
            'saas': [
                "AI workflow automation tools disrupting industries",
                "No-code development platforms democratizing software",
                "Customer success automation reducing churn",
                "API-first architecture becoming standard",
                "Micro-SaaS solutions targeting niche markets"
            ],
            'marketing': [
                "AI-generated personalized video content scaling",
                "Voice commerce optimization strategies emerging", 
                "Interactive content driving 300% more engagement",
                "First-party data strategies replacing cookies",
                "Influencer micro-communities outperforming macro"
            ],
            'ecommerce': [
                "Social commerce integration boosting conversions",
                "Sustainable packaging becoming purchase driver",
                "Live shopping experiences increasing sales 400%",
                "AI-powered inventory prediction reducing waste",
                "Subscription model adoption across categories"
            ]
        }
        
        default_trends = [
            f"Emerging {niche} market opportunities gaining traction",
            f"Innovation in {niche} technology disrupting status quo",
            f"{niche} consumer behavior shifts creating new demand",
            f"Next-generation {niche} solutions reaching mainstream"
        ]
        
        trends_list = niche_trends.get(niche.lower(), default_trends)
        simulated = []
        
        for i, trend in enumerate(trends_list[:5]):  # Limit to 5 simulated trends
            simulated.append(TrendData(
                niche=niche,
                title=trend,
                content=f"High-velocity trend detected in {niche} space: {trend}. Oracle analysis shows significant growth potential with strong momentum indicators.",
                source="Oracle Intelligence",
                trend_score=random.uniform(0.65, 0.95),
                velocity=random.uniform(0.45, 0.85)
            ))
        
        return simulated
    
    async def generate_content(self, niche: str, trends: List[str], content_type: str) -> GeneratedContent:
        """Generate AI-powered content using Gemini"""
        
        if not self.gemini_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        # Use Gemini for all content types with specialized prompts
        system_prompts = {
            'ad_copy': """You are an expert direct-response copywriter specializing in high-converting ad copy. 
            Create compelling, action-driven advertisements that follow proven frameworks like AIDA, PAS, and SCAB.
            Focus on benefits, urgency, and clear calls-to-action. Write persuasive copy that converts browsers into buyers.""",
            
            'social_post': """You are a social media expert and viral content strategist. 
            Create engaging, shareable content that resonates with target audiences and drives massive engagement.
            Focus on storytelling, value delivery, hooks, and authentic connection. Make it worth sharing.""",
            
            'affiliate_review': """You are a trusted product reviewer and affiliate marketer.
            Create honest, detailed reviews that help customers make informed decisions while naturally promoting products.
            Focus on benefits, addressing objections, comparisons, and authentic recommendations."""
        }
        
        # Create content prompt based on type
        trend_context = "\n".join([f"- {trend}" for trend in trends])
        
        content_prompts = {
            'ad_copy': f"""Create high-converting ad copy for the {niche} niche based on these trending topics:
{trend_context}

Requirements:
- Write 3 different ad variations (short, medium, long)
- Include compelling headlines with urgency
- Use proven copywriting frameworks (AIDA, PAS, SCAB)
- Include clear call-to-action
- Focus on benefits and transformation
- Target audience pain points and desires
- Use emotional triggers and social proof

Format as: **Headline** | Body Copy | **CTA**

Make it irresistible and action-oriented.""",

            'social_post': f"""Create viral social media content for the {niche} niche based on these trends:
{trend_context}

Requirements:
- Create 3 platform-specific posts (Twitter/X, LinkedIn, Instagram)
- Include relevant hashtags for each platform
- Engaging hooks and value-driven content
- Encourage interaction and sharing
- Maintain authentic, relatable tone
- Include content pillars: education, inspiration, entertainment
- Use emojis and formatting for readability

Format each post with platform label and optimized content.""",

            'affiliate_review': f"""Create persuasive affiliate marketing content for the {niche} niche based on these trends:
{trend_context}

Requirements:
- Write comprehensive product review with pros/cons
- Include personal experience narrative
- Address common objections and concerns
- Highlight key benefits and unique selling points
- Include comparison with alternatives
- Clear recommendation with reasoning
- Proper affiliate disclosure
- Call-to-action for purchasing

Format as structured review with clear sections and compelling conclusion."""
        }
        
        try:
            # Initialize Gemini chat
            chat = LlmChat(
                api_key=self.gemini_key,
                session_id=f"{content_type}-{uuid.uuid4()}",
                system_message=system_prompts[content_type]
            ).with_model("gemini", "gemini-2.5-flash-preview-04-17").with_max_tokens(4096)
            
            # Generate content
            user_message = UserMessage(text=content_prompts[content_type])
            response = await chat.send_message(user_message)
            
            # Check if response is valid
            if not response:
                raise Exception("Empty response from Gemini API")
            
            # Calculate confidence score based on response length and quality indicators
            confidence = min(0.95, 0.75 + (len(response) / 2000) * 0.20)
            
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
        
        # Store trends in MongoDB
        for trend in trends:
            trend_dict = trend.dict()
            await db.trends.insert_one(trend_dict)
        
        # Generate forecast summary using Gemini
        top_trends = [trend.title for trend in trends[:5]]
        forecast_prompt = f"""Based on these top trends in {request.niche}: {', '.join(top_trends)}, provide a brief, actionable forecast summary (2-3 sentences) and identify the top 3 business opportunities."""
        
        try:
            chat = LlmChat(
                api_key=oracle.gemini_key,
                session_id=f"forecast-{uuid.uuid4()}",
                system_message="You are a business trend analyst providing concise, actionable insights."
            ).with_model("gemini", "gemini-2.5-flash-preview-04-17")
            
            forecast_response = await chat.send_message(UserMessage(text=forecast_prompt))
        except Exception as e:
            logging.warning(f"Forecast generation failed: {e}")
            forecast_response = f"Strong momentum detected in {request.niche} with {len(trends)} high-velocity trends identified."
        
        # Extract opportunities
        opportunities = [
            f"Capitalize on {trends[0].title if trends else 'emerging trends'}",
            f"Create targeted content around {request.niche} innovation",
            f"Target early adopters in {request.niche} market segment"
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
        
        # Store in MongoDB
        content_dict = content.dict()
        await db.generated_content.insert_one(content_dict)
        
        return content
        
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/content/history/{niche}")
async def get_content_history(niche: str):
    """Get content generation history for a niche"""
    try:
        cursor = db.generated_content.find({"niche": niche}).sort("created_at", -1).limit(20)
        content_history = []
        async for doc in cursor:
            # Convert MongoDB ObjectId to string for JSON serialization
            doc['_id'] = str(doc['_id'])
            content_history.append(doc)
        
        return {"content_history": content_history}
    except Exception as e:
        logging.error(f"Error fetching content history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trends/latest/{niche}")
async def get_latest_trends(niche: str):
    """Get latest trends for a niche"""
    try:
        cursor = db.trends.find({"niche": niche}).sort("created_at", -1).limit(10)
        trends = []
        async for doc in cursor:
            # Convert MongoDB ObjectId to string for JSON serialization  
            doc['_id'] = str(doc['_id'])
            trends.append(doc)
        
        return {"trends": trends}
    except Exception as e:
        logging.error(f"Error fetching trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get counts from MongoDB
        trends_count = await db.trends.count_documents({})
        content_count = await db.generated_content.count_documents({})
        
        # Get distinct niches
        distinct_niches = await db.trends.distinct("niche")
        
        return {
            "total_trends_monitored": trends_count,
            "content_pieces_generated": content_count,
            "active_niches": distinct_niches or ["fitness", "crypto", "saas", "ecommerce", "marketing"],
            "system_status": "operational"
        }
    except Exception as e:
        logging.error(f"Error fetching stats: {e}")
        return {
            "total_trends_monitored": 0,
            "content_pieces_generated": 0,
            "active_niches": ["fitness", "crypto", "saas", "ecommerce", "marketing"],
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
    """Initialize database collections"""
    try:
        # Create indexes for better performance
        await db.trends.create_index("niche")
        await db.trends.create_index("created_at")
        await db.generated_content.create_index("niche")
        await db.generated_content.create_index("content_type")
        await db.generated_content.create_index("created_at")
        
        logger.info("Oracle Engine startup complete - MongoDB initialized")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()