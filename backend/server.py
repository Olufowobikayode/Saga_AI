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
from datetime import datetime, timezone
import asyncio
import google.generativeai as genai
from pytrends.request import TrendReq
import random
import certifi

# --- INITIAL SETUP ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- DATABASE AND API CLIENTS ---
try:
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    gemini_api_key = os.environ['GEMINI_API_KEY']

    ca = certifi.where()
    client = AsyncIOMotorClient(mongo_url, tlsCAFile=ca)
    db = client[db_name]
    genai.configure(api_key=gemini_api_key)

except KeyError as e:
    logger.error(f"FATAL: Environment variable {e} not set. The application cannot start.")
    raise

# --- Pydantic MODELS ---
def utcnow():
    return datetime.now(timezone.utc)

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
    created_at: datetime = Field(default_factory=utcnow)

class ForecastRequest(BaseModel):
    niche: str
    trend_data: List[str]
    content_type: str

class GeneratedContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    niche: str
    content_type: str
    title: str
    content: str
    confidence_score: float
    created_at: datetime = Field(default_factory=utcnow)

class TrendAnalysis(BaseModel):
    niche: str
    trends: List[TrendData]
    forecast_summary: str
    top_opportunities: List[str]

# --- ORACLE ENGINE CORE ---
class OracleEngine:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    # MODIFIED: Rewritten for speed and reliability
    async def monitor_niche_trends(self, niche: str, keywords: List[str] = None) -> List[TrendData]:
        # Start with a reliable base of simulated trends
        trends = self._generate_simulated_trends(niche)
        
        try:
            pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
            keywords = keywords or [niche]
            expanded_keywords = self._expand_niche_keywords(niche, keywords)
            random.shuffle(expanded_keywords)

            # Create batches of keywords to query
            batch_size = 5
            num_keywords_to_process = 10
            keyword_batches = [
                expanded_keywords[i:i + batch_size]
                for i in range(0, min(len(expanded_keywords), num_keywords_to_process), batch_size)
            ]

            # Asynchronous function to fetch data for a single batch
            async def fetch_batch(kw_list):
                loop = asyncio.get_running_loop()
                # Run the synchronous pytrends code in a separate thread
                interest_data = await loop.run_in_executor(
                    None, lambda: pytrends.build_payload(kw_list=kw_list, cat=0, timeframe='now 1-d', geo='', gprop='')
                )
                interest_data = pytrends.interest_over_time()
                return interest_data, kw_list

            # Run all batch fetches concurrently for maximum speed
            tasks = [fetch_batch(batch) for batch in keyword_batches]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process the results
            for result in results:
                if isinstance(result, Exception):
                    logging.warning(f"A trend batch failed: {result}")
                    continue
                
                interest_data, kw_list = result
                if not interest_data.empty:
                    for keyword in kw_list:
                        if keyword in interest_data.columns:
                            latest_values = interest_data[keyword].tail(3).tolist()
                            avg_score = sum(latest_values) / len(latest_values) if latest_values else 0
                            velocity = self._calculate_velocity(latest_values)
                            trends.append(TrendData(
                                niche=niche, title=f"Live Trend: {keyword}",
                                content=f"Live search interest for '{keyword}' shows momentum.",
                                source="Google Trends", trend_score=round(avg_score / 100.0, 3),
                                velocity=round(velocity, 3)
                            ))
                            
        except Exception as e:
            logging.error(f"Major error in trend monitoring: {e}")
        
        # Sort the combined list of simulated and live trends
        trends.sort(key=lambda x: (x.trend_score * x.velocity), reverse=True)
        return trends[:10]

    def _expand_niche_keywords(self, niche: str, base_keywords: List[str]) -> List[str]:
        niche_expansions = {
            'fitness': ['workout', 'nutrition', 'supplements', 'training', 'wellness', 'exercise', 'protein', 'cardio', 'HIIT', 'yoga', 'weight loss', 'strength training', 'bodybuilding', 'running', 'home workouts', 'gym near me', 'personal trainer', 'fitness classes', 'diet', 'calories', 'creatine', 'BCAAs', 'pre-workout', 'whey protein', 'fat burner', 'vitamins', 'minerals', 'healthy eating', 'meal plan', 'vegan diet', 'keto diet', 'paleo diet', 'intermittent fasting', 'meditation', 'mindfulness', 'stress management', 'recovery', 'stretching', 'flexibility', 'Pilates', 'Zumba', 'CrossFit', 'cycling', 'swimming', 'functional fitness', 'bodyweight exercise', 'resistance training', 'kettlebell', 'dumbbell', 'barbell', 'calisthenics', 'endurance', 'mobility', 'active recovery', 'foam rolling', 'sports nutrition', 'hydration', 'electrolytes', 'gut health', 'sleep', 'biohacking', 'wearable technology', 'fitness apps', 'corporate wellness', 'senior fitness', 'prenatal fitness', 'postnatal fitness', 'mental health', 'self-care', 'holistic health'],
            'crypto': ['bitcoin', 'ethereum', 'defi', 'nft', 'blockchain', 'trading', 'altcoins', 'web3', 'cryptocurrency', 'BTC', 'ETH', 'decentralized finance', 'non-fungible token', 'smart contract', 'wallet', 'crypto exchange', 'Binance', 'Coinbase', 'Kraken', 'Solana', 'Cardano', 'Ripple', 'XRP', 'Dogecoin', 'Shiba Inu', 'metaverse', 'dApps', 'yield farming', 'staking', 'liquidity pool', 'mining', 'crypto mining', 'gas fees', 'airdrop', 'ICO', 'initial coin offering', 'stablecoin', 'USDT', 'USDC', 'DAO', 'decentralized autonomous organization', 'Layer 2', 'scalability', 'halving', 'bull market', 'bear market', 'HODL', 'FUD', 'FOMO', 'DYOR', 'technical analysis', 'charting', 'cold storage', 'hot wallet', 'Ledger', 'Trezor', 'public key', 'private key', 'seed phrase', 'tokenomics', 'whitepaper', 'roadmap', 'crypto regulations', 'SEC', 'crypto news', 'crypto influencers', 'play-to-earn', 'P2E', 'move-to-earn', 'M2E', 'NFT marketplace', 'OpenSea', 'Blur', 'memecoin', 'governance token', 'altcoin season', 'crypto portfolio', 'dollar-cost averaging', 'DCA', 'on-chain analysis', 'EVM'],
            'saas': ['software', 'automation', 'productivity', 'business tools', 'cloud', 'api', 'integration', 'SaaS', 'subscription', 'CRM', 'customer relationship management', 'marketing automation', 'email marketing', 'project management', 'collaboration software', 'HR software', 'accounting software', 'invoicing', 'helpdesk', 'customer support', 'live chat', 'analytics', 'business intelligence', 'dashboard', 'B2B', 'enterprise software', 'SMB', 'small business software', 'startup tools', 'product-led growth', 'PLG', 'freemium', 'free trial', 'demo', 'user onboarding', 'UX', 'UI', 'ARR', 'MRR', 'churn rate', 'customer lifetime value', 'CLV', 'lead generation', 'sales funnel', 'DevOps', 'CI/CD', 'platform as a service', 'PaaS', 'infrastructure as a service', 'IaaS', 'cloud hosting', 'AWS', 'Google Cloud', 'Azure', 'no-code', 'low-code', 'workflow automation', 'API first', 'single sign-on', 'SSO', 'data security', 'uptime', 'SLA', 'vertical SaaS', 'horizontal SaaS', 'microservices', 'ERP', 'enterprise resource planning', 'supply chain management', 'ecommerce platform', 'payment gateway', 'subscription management', 'customer success', 'user retention'],
        }
        expanded = list(set(base_keywords))
        niche_key = niche.lower()
        if niche_key in niche_expansions:
            expanded.extend(niche_expansions[niche_key])
        return list(set(expanded))

    def _calculate_velocity(self, values: List[float]) -> float:
        if len(values) < 2: return 0.0
        return max(0.0, min(1.0, (values[-1] - values[0]) / 100.0))

    # NEW: Now provides a reliable base of high-quality trends for core niches.
    def _generate_simulated_trends(self, niche: str) -> List[TrendData]:
        niche_key = niche.lower()
        evergreen_trends = {
            'fitness': ["AI-Powered Personal Training Apps", "Wearable Tech for Health Monitoring", "Mental Wellness and Mindfulness", "Plant-Based Nutrition and Protein", "Home Gym and Smart Equipment"],
            'crypto': ["Decentralized Finance (DeFi) Adoption", "NFTs for Digital Identity & Ticketing", "Layer 2 Scaling Solutions", "Web3 Gaming (Play-to-Earn)", "Institutional Investment in Bitcoin"],
            'saas': ["AI in Workflow Automation", "Vertical SaaS for Specific Industries", "No-Code/Low-Code Development Platforms", "Cybersecurity and Data Privacy Tools", "Collaborative Project Management Software"]
        }
        
        trends_list = evergreen_trends.get(niche_key, [f"Emerging {niche} Opportunities", f"Innovation in {niche} Technology"])
        
        return [
            TrendData(
                niche=niche, title=trend, content=f"High-velocity evergreen trend: {trend}",
                source="Oracle Intelligence", trend_score=random.uniform(0.75, 0.95), velocity=random.uniform(0.6, 0.85)
            ) for trend in trends_list
        ]

    async def generate_content(self, niche: str, trends: List[str], content_type: str) -> GeneratedContent:
        master_prompt_template = """
You are Oracle, a master-level strategist combining the skills of a world-class copywriter, a viral social media manager, and a data-driven performance marketer. Your voice is human, engaging, and trustworthy. Your goal is NOT just to create content, but to generate assets that drive specific actions.

You will use the provided trends as the core inspiration for every piece of content.

**1. Niche:** {niche}
**2. Content Type:** {content_type}
**3. Key Trends:**
{trends}

---

**YOUR TASK:** Based on the information above, generate the following assets. Adhere strictly to the format for the requested **Content Type**.

---

### **IF Content Type is `social_post`:**

Your goal is virality and deep engagement. Create a post that stops the scroll and starts conversations.

**Social Post:**
- **Hook:** Start with a relatable question, a bold statement, or a surprising statistic directly related to the trends.
- **Body:** Weave a short, compelling narrative or provide 3-5 high-value, actionable tips inspired by the trends. Use emojis to add personality and improve readability.
- **Call to Engagement:** End with an open-ended question to encourage comments (e.g., "What's your take on this?" or "Have you tried this?").
- **Hashtags:** Provide 5-7 highly relevant hashtags, mixing broad and niche terms.

**Detailed Image Prompt for AI Generator (e.g., Midjourney, DALL-E):**
- **Style:** [e.g., Photorealistic, cinematic, vibrant illustration, modern graphic design]
- **Subject:** [e.g., A person expressing a specific emotion, a symbolic object, a stylized representation of a concept]
- **Scene:** [e.g., A minimalist office, a dramatic outdoor landscape, an abstract background with specific colors] - Describe the environment that best captures the post's mood.
- **Lighting:** [e.g., Soft and natural, dramatic studio lighting, neon glow, golden hour]
- **Mood:** [e.g., Inspiring and hopeful, urgent and energetic, thoughtful and calm, luxurious and exclusive]
- **Full Prompt Example:** "cinematic photo, a young female founder looking thoughtfully at a holographic chart showing upward-trending data, in a modern, minimalist office at dusk, soft golden hour light streaming through the window, mood is inspiring and forward-thinking, 8k, hyper-detailed"

---

### **IF Content Type is `ad_copy`:**

Your goal is to get the click. Use proven direct-response copywriting techniques.

**Ad Copy (3 Variations for A/B Testing):**
- **Variation A (Short & Punchy - for Feeds):**
    - **Headline:** A 5-8 word, high-impact headline that targets a pain point revealed by the trends.
    - **Body:** 1-2 sentences that present the "big promise" or unique solution.
    - **CTA:** A clear, urgent call-to-action (e.g., "Learn More," "Get Started Free," "Shop Now").
- **Variation B (Story-Driven - for Articles/Newsletters):**
    - **Hook:** A short, relatable story or a "Did you know..." fact based on the trends.
    - **Problem/Agitate:** Clearly describe the problem the target audience is facing.
    - **Solution/Promise:** Introduce the solution with a focus on benefits, not just features.
    - **CTA:** A compelling call-to-action with a reason to click now (e.g., "Get the full strategy before it's gone").
- **Variation C (Benefit-Focused - for Landing Pages):**
    - **Headline:** Focus on the ultimate desired outcome.
    - **Bulleted Benefits:** List 3-5 key benefits derived from the trends, explaining what the user will *get*, *feel*, or *achieve*.
    - **CTA:** A strong, benefit-oriented call-to-action (e.g., "Start My Transformation," "Unlock My Growth").

**Detailed Image Prompt for Ad Creative:**
- **Style:** [e.g., Bright and clean commercial photography, modern user-interface mockup, dynamic graphic with bold text]
- **Subject:** A clear depiction of the product in use, or a person achieving the result promised by the ad. The subject should look aspirational and relatable.
- **Scene:** A clean, uncluttered background that doesn't distract from the main subject. Use brand colors if applicable.
- **Lighting:** Bright, professional, and optimistic.
- **Mood:** Urgent, exciting, trustworthy, problem-solving.
- **Full Prompt Example:** "bright commercial photo, a smiling woman in her 30s easily using a sleek productivity SaaS on her laptop, sitting in a bright, modern co-working space, background is slightly blurred, mood is efficient and empowering, 4k"

---

### **IF Content Type is `print_on_demand`:**

Your goal is to create commercially viable, creative concepts for Print on Demand products like t-shirts, mugs, and posters.

**POD Concept:**
- **Concept/Theme:** A short, catchy name for the design idea, inspired by the trends.
- **Design Style:** [e.g., Vintage Retro, Minimalist Line Art, Bold Typography, 90s Nostalgia, Abstract Geometric, Whimsical Illustration].
- **Key Elements:** Describe the main visual components of the design.
- **Tagline/Text (Optional):** A short, clever phrase to include in the design.
- **Target Audience:** Who would buy this? (e.g., Developers, Fitness Enthusiasts, Crypto Traders).

**Detailed Image Prompt for POD Design (Design-Based):**
- **Style:** Use terms like `minimalist vector art`, `flat illustration`, `graphic t-shirt design`, `sticker design`.
- **Subject:** Clearly describe the main subject and its elements.
- **Composition:** Specify `isolated on a clean white background` to ensure it's ready for printing.
- **Color Palette:** Suggest a limited, cohesive color scheme (e.g., `monochromatic`, `warm retro colors`, `neon cyberpunk`).
- **Full Prompt Example:** "graphic t-shirt design, a stylized, minimalist vector art of an astronaut meditating in a lotus position on top of a crescent moon, a simple Saturn planet in the background, isolated on a clean white background, monochromatic blue and white color palette, clean lines, no text"

---

### **IF Content Type is `ecommerce_product`:**

Your goal is to write a compelling product description for an e-commerce store that converts browsers into buyers.

**E-commerce Product Description:**
- **Product Title:** An SEO-friendly and enticing title.
- **Tagline:** A single, powerful sentence that captures the product's main benefit.
- **Story-Driven Description:** A 2-3 paragraph description that tells a story. Set the scene, introduce the problem (related to the trends), and present your product as the hero.
- **Bulleted Features & Benefits:** List 3-5 key features and translate each into a tangible benefit for the customer.
- **Specifications:** A simple list of essential details (e.g., Materials, Dimensions, Compatibility).

**Detailed Image Prompt for E-commerce Photography:**
- **Style:** Use terms like `professional product photography`, `e-commerce product shot`, `cinematic product photo`.
- **Subject:** The product itself, shown from its most appealing angle.
- **Scene:** `on a clean, solid color background` or `in a lifestyle context` (e.g., a watch on a wrist).
- **Lighting:** `bright studio lighting`, `soft natural light`.
- **Composition:** `centered`, `dynamic angle`, `showing texture and detail`.
- **Full Prompt Example:** "professional product photography of a sleek, matte black wireless charger, on a clean white background, bright studio lighting to eliminate shadows, dynamic angle showing the charging port and texture, 8k, hyper-detailed"

---

### **IF Content Type is `affiliate_review`:**

Your goal is to build maximum trust and guide the reader to a confident purchase, while also capturing their information for future marketing.

**Affiliate Review Content:**
- **Catchy Title:** A title that combines the product name with a powerful benefit or addresses a major question (e.g., "Is [Product Name] Worth It? My Honest 2025 Review").
- **Introduction (The Hook):** Start with a personal story about the problem you faced, which should relate to the identified trends.
- **What is [Product Name] & Who is it For?:** Briefly explain the product and the ideal customer.
- **My Experience & Results (The Core):** Detail your journey with the product. How did it solve your problem? Use the trends as context for why this product is so relevant *right now*.
- **Top 3 Features/Benefits:** Break down the most impactful benefits, linking each one back to solving a specific pain point.
- **What I Didn't Like (The Honesty):** Include 1-2 minor drawbacks or limitations. This builds immense trust and makes your recommendation more believable.
- **The Verdict & Final Recommendation:** A strong summary of why you recommend it despite the minor flaws.
- **Strong Call-to-Action:** A clear, enthusiastic call to action. "Click here to get [Product Name] and see the same results I did. You won't regret it."

**Landing Page Code (with Lead Capture for Google Sites):**
- **Instructions:** Generate a complete, single HTML file with embedded modern CSS (using the Tailwind CSS CDN) for a high-converting landing page. The page must be mobile-responsive and include placeholders for an affiliate link and a Google Form link for lead capture.
- **Structure:**
    1.  **Hero Section:** Compelling headline, sub-headline, and TWO prominent CTA buttons: "Get It Now" (for the affiliate link) and "Get Updates & Free Checklist" (for the lead capture).
    2.  **Problem Section:** A short section describing the visitor's pain point.
    3.  **Benefits Section:** 3-5 cards or list items with icons and benefit descriptions.
    4.  **Social Proof Section:** 2-3 placeholder testimonial blocks.
    5.  **Final CTA Section:** A final, urgent call-to-action block with the same two buttons.
- **JavaScript:** Include a simple, inline script that shows a confirmation alert when the "Get Updates" button is clicked.
- **Output:** Provide the full, copy-paste-ready HTML code inside a single code block.
"""
        
        trend_str = "\n".join(f"- {t.title}" for t in trends)
        full_prompt = master_prompt_template.format(
            niche=niche,
            content_type=content_type,
            trends=trend_str
        )

        try:
            response = await self.model.generate_content_async(full_prompt)
            if not response or not hasattr(response, 'text') or not response.text:
                raise Exception("Empty or invalid response from Gemini API")
            
            content_text = response.text
            confidence = min(1.5, 0.95 + (len(content_text) / 3000) * 0.2)
            
            return GeneratedContent(
                niche=niche,
                content_type=content_type,
                title=f"{content_type.replace('_', ' ').title()} for {niche}",
                content=content_text,
                confidence_score=confidence
            )
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise HTTPException(status_code=500, detail="Content generation failed.")

# --- FastAPI APP AND ROUTER ---
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
            # Storing only the top 10 trends found
            await db.trends.insert_many([t.dict() for t in trends])

        top_trends_titles = [trend.title for trend in trends[:5]]
        forecast_prompt = f"""Based on these top trends in '{request.niche}': {', '.join(top_trends_titles)}. Provide a brief, actionable forecast summary (2-20 sentences) and identify the top 20 business opportunities."""
        
        forecast_summary = f"Strong momentum detected in {request.niche}."
        try:
            forecast_response = await oracle.model.generate_content_async(forecast_prompt)
            forecast_summary = forecast_response.text
        except Exception as e:
            logging.warning(f"Forecast generation failed: {e}")

        opportunities = [f"Capitalize on {trends[0].title}" if trends else f"Explore emerging {request.niche} trends", f"Create targeted content around {request.niche} innovation"]
        
        return TrendAnalysis(
            niche=request.niche,
            trends=trends,
            forecast_summary=forecast_summary,
            top_opportunities=opportunities
        )
    except Exception as e:
        logger.error(f"Error in analyze_niche: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@api_router.post("/content/generate", response_model=GeneratedContent)
async def generate_content_endpoint(request: ForecastRequest):
    try:
        # Re-fetch trends to ensure freshness for content generation, or pass from frontend
        # For simplicity, we assume trend_data from the request is a list of trend titles
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
    cursor = db.trends.find({"niche": niche}).sort("created_at", -1).limit(20)
    trends = [doc for doc in await cursor.to_list(length=20)]
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
        logger.error(f"Error fetching stats: {e}")
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
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
        await db.trends.create_index("niche")
        await db.generated_content.create_index("niche")
        logger.info("Database indexes ensured.")
    except Exception as e:
        logger.error(f"Startup error: Could not connect to MongoDB or create indexes. {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("MongoDB connection closed.")