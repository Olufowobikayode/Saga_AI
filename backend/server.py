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

    async def _fetch_and_process_trends(self, niche: str, keywords: List[str]) -> List[TrendData]:
        """A helper function to fetch and process trends for a given list of keywords."""
        trends = []
        if not keywords:
            return trends

        try:
            pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
            random.shuffle(keywords)

            batch_size = 5
            num_keywords_to_process = 10
            keyword_batches = [
                keywords[i:i + batch_size]
                for i in range(0, min(len(keywords), num_keywords_to_process), batch_size)
            ]

            async def fetch_batch(kw_list):
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    None, lambda: pytrends.build_payload(kw_list=kw_list, cat=0, timeframe='now 1-d', geo='', gprop='')
                )
                interest_data = pytrends.interest_over_time()
                return interest_data, kw_list

            tasks = [fetch_batch(batch) for batch in keyword_batches]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    logging.warning(f"A trend batch failed for niche '{niche}': {result}")
                    continue
                interest_data, kw_list = result
                if not interest_data.empty:
                    for keyword in kw_list:
                        if keyword in interest_data.columns:
                            latest_values = interest_data[keyword].tail(3).tolist()
                            avg_score = sum(latest_values) / len(latest_values) if latest_values else 0
                            velocity = self._calculate_velocity(latest_values)
                            if avg_score > 0: # Only add trends with some interest
                                trends.append(TrendData(
                                    niche=niche, title=f"Live Trend: {keyword}",
                                    content=f"Live search interest for '{keyword}' shows momentum.",
                                    source="Google Trends", trend_score=round(avg_score / 100.0, 3),
                                    velocity=round(velocity, 3)
                                ))
        except Exception as e:
            logging.error(f"Major error during live trend monitoring for '{niche}': {e}")
        
        return trends

    # NEW: This is the primary function, now relying 100% on live data with a fallback.
    async def monitor_niche_trends(self, niche: str, keywords: List[str] = None) -> List[TrendData]:
        # First, try to get trends with the specific keywords provided
        primary_keywords = self._expand_niche_keywords(niche, keywords)
        live_trends = await self._fetch_and_process_trends(niche, primary_keywords)

        # **INTELLIGENT FALLBACK**
        # If the primary search yields no results, do a broader search on the niche name itself.
        if not live_trends:
            logger.warning(f"Primary keyword search for '{niche}' returned no results. Trying a broad search.")
            broad_keywords = [niche]
            live_trends = await self._fetch_and_process_trends(niche, broad_keywords)
        
        if not live_trends:
            logger.error(f"All trend searches failed for niche '{niche}'. No data to return.")
            # Return an empty list, which the frontend can handle gracefully.
            return []

        live_trends.sort(key=lambda x: (x.trend_score * x.velocity), reverse=True)
        return live_trends[:20] # Return up to 20 top trends found

    def _expand_niche_keywords(self, niche: str, base_keywords: List[str]) -> List[str]:
        # This function remains the same, providing a rich list of potential keywords.
        niche_expansions = {
            'fitness': ['workout', 'nutrition', 'supplements', 'training', 'wellness', 'exercise', 'protein', 'cardio', 'HIIT', 'yoga', 'weight loss', 'strength training', 'bodybuilding', 'running', 'home workouts', 'gym near me', 'personal trainer', 'fitness classes', 'diet', 'calories', 'creatine', 'BCAAs', 'pre-workout', 'whey protein', 'fat burner', 'vitamins', 'minerals', 'healthy eating', 'meal plan', 'vegan diet', 'keto diet', 'paleo diet', 'intermittent fasting', 'meditation', 'mindfulness', 'stress management', 'recovery', 'stretching', 'flexibility', 'Pilates', 'Zumba', 'CrossFit', 'cycling', 'swimming', 'functional fitness', 'bodyweight exercise', 'resistance training', 'kettlebell', 'dumbbell', 'barbell', 'calisthenics', 'endurance', 'mobility', 'active recovery', 'foam rolling', 'sports nutrition', 'hydration', 'electrolytes', 'gut health', 'sleep', 'biohacking', 'wearable technology', 'fitness apps', 'corporate wellness', 'senior fitness', 'prenatal fitness', 'postnatal fitness', 'mental health', 'self-care', 'holistic health'],
            'crypto': ['bitcoin', 'ethereum', 'defi', 'nft', 'blockchain', 'trading', 'altcoins', 'web3', 'cryptocurrency', 'BTC', 'ETH', 'decentralized finance', 'non-fungible token', 'smart contract', 'wallet', 'crypto exchange', 'Binance', 'Coinbase', 'Kraken', 'Solana', 'Cardano', 'Ripple', 'XRP', 'Dogecoin', 'Shiba Inu', 'metaverse', 'dApps', 'yield farming', 'staking', 'liquidity pool', 'mining', 'crypto mining', 'gas fees', 'airdrop', 'ICO', 'initial coin offering', 'stablecoin', 'USDT', 'USDC', 'DAO', 'decentralized autonomous organization', 'Layer 2', 'scalability', 'halving', 'bull market', 'bear market', 'HODL', 'FUD', 'FOMO', 'DYOR', 'technical analysis', 'charting', 'cold storage', 'hot wallet', 'Ledger', 'Trezor', 'public key', 'private key', 'seed phrase', 'tokenomics', 'whitepaper', 'roadmap', 'crypto regulations', 'SEC', 'crypto news', 'crypto influencers', 'play-to-earn', 'P2E', 'move-to-earn', 'M2E', 'NFT marketplace', 'OpenSea', 'Blur', 'memecoin', 'governance token', 'altcoin season', 'crypto portfolio', 'dollar-cost averaging', 'DCA', 'on-chain analysis', 'EVM'],
            'saas': ['software', 'automation', 'productivity', 'business tools', 'cloud', 'api', 'integration', 'SaaS', 'subscription', 'CRM', 'customer relationship management', 'marketing automation', 'email marketing', 'project management', 'collaboration software', 'HR software', 'accounting software', 'invoicing', 'helpdesk', 'customer support', 'live chat', 'analytics', 'business intelligence', 'dashboard', 'B2B', 'enterprise software', 'SMB', 'small business software', 'startup tools', 'product-led growth', 'PLG', 'freemium', 'free trial', 'demo', 'user onboarding', 'UX', 'UI', 'ARR', 'MRR', 'churn rate', 'customer lifetime value', 'CLV', 'lead generation', 'sales funnel', 'DevOps', 'CI/CD', 'platform as a service', 'PaaS', 'infrastructure as a service', 'IaaS', 'cloud hosting', 'AWS', 'Google Cloud', 'Azure', 'no-code', 'low-code', 'workflow automation', 'API first', 'single sign-on', 'SSO', 'data security', 'uptime', 'SLA', 'vertical SaaS', 'horizontal SaaS', 'microservices', 'ERP', 'enterprise resource planning', 'supply chain management', 'ecommerce platform', 'payment gateway', 'subscription management', 'customer success', 'user retention'],
        }
        expanded = list(set(base_keywords or []))
        niche_key = niche.lower()
        if niche_key in niche_expansions:
            expanded.extend(niche_expansions[niche_key])
        return list(set(expanded))

    def _calculate_velocity(self, values: List[float]) -> float:
        if len(values) < 2: return 0.0
        return max(0.0, min(1.0, (values[-1] - values[0]) / 100.0))
    async def generate_content(self, niche: str, trends: List[str], content_type: str) -> GeneratedContent:
        master_prompt_template = """
You are Oracle, a world-class growth-hacking CMO with deep expertise in copywriting, neuro-marketing, and viral content strategy. Your sole mission is to generate ready-to-publish assets designed for explosive growth, massive engagement, and high-conversion sales. Every word you write is intentional and backed by proven marketing principles.

You will use the provided trends as the core insight to create timely, relevant, and irresistible content.

**1. Niche:** {niche}
**2. Content Type:** {content_type}
**3. Key Trends:**
{trends}

---

**YOUR TASK:** Based on the information above, generate the following high-performance assets. Adhere strictly to the professional format requested for the **Content Type**.

---

### **IF Content Type is `facebook_post`:**

**Goal:** Spark high-quality engagement and build a loyal community. Use a conversational, AIDA (Attention, Interest, Desire, Action) structure.

**Facebook Post:**
- **Attention (Hook):** Start with a bold, relatable question or a pattern-interrupting statement based on a key trend. Make them stop scrolling.
- **Interest (Story/Value):** Tell a short, personal story or provide a surprising insight related to the trends. Build an immediate connection.
- **Desire (Benefit):** Explain the powerful benefit of embracing this trend or idea. What positive future can the reader achieve? Paint a vivid picture.
- **Action (Call to Engagement):** End with a specific, low-friction question that encourages detailed comments, not just "yes/no" answers. (e.g., "What's the #1 thing holding you back from trying this?").
- **Hashtags:** Provide 3-5 highly relevant, community-focused hashtags.

**Image Prompt (Thumb-Stopping Visual):**
- **Style:** "Vibrant, high-contrast, lifestyle photography".
- **Subject:** A person (or people) experiencing the peak positive emotion associated with the post's "Desire" stage. Action-oriented and relatable.
- **Full Prompt Example:** "Vibrant lifestyle photo, a group of diverse friends laughing together during a home workout, sunlight streaming in, feeling energetic and connected, shot on a professional DSLR camera, 8k"

---

### **IF Content Type is `twitter_thread`:**

**Goal:** Go viral by providing immense value in a structured, easy-to-read thread.

**Twitter (X) Thread:**
- **Tweet 1 (The Hook):** A bold, contrarian take or a massive promise. e.g., "I analyzed [Niche] for 100 hours. Here are 5 trends that will make or break your business in the next 6 months. 🧵". End with the thread emoji.
- **Tweet 2 (The Problem):** Describe the current, painful problem that the audience is facing, using insights from the trends.
- **Tweet 3-5 (The Value):** Each tweet should be a self-contained, actionable tip or insight that solves a piece of the problem. Use bullet points, emojis, and whitespace for maximum readability.
- **Tweet 6 (The Summary):** A "TL;DR" that summarizes the key takeaways from the thread.
- **Tweet 7 (The Engagement/CTA):** Ask a question to spark debate or direct followers to a link.

**Image Prompt (Diagram/Graphic):**
- **Style:** "Clean, minimalist infographic, vector illustration".
- **Subject:** A simple visual representation of the thread's core concept (e.g., a simple 3-step process, a before-and-after diagram).
- **Full Prompt Example:** "minimalist infographic, a simple 3-panel cartoon showing a sad stick figure with a problem, then a lightbulb icon, then a happy stick figure with a solution, clean lines, using only blue and white colors, isolated on a white background"

---

### **IF Content Type is `linkedin_article`:**

**Goal:** Establish authority and generate professional leads. Use a structured, data-driven, and insightful tone.

**LinkedIn Article:**
- **Headline:** A professional, benefit-driven headline. e.g., "Beyond the Hype: 3 Actionable [Niche] Trends Our Data Shows Are Driving Real ROI".
- **Executive Summary:** A short, bolded paragraph at the top summarizing the article's key takeaway for busy professionals.
- **Introduction:** Set the scene and state the core problem or opportunity based on the trends.
- **Section 1, 2, 3 (The Body):** Each section should be a deep dive into a specific trend. Use subheadings (H2s), bullet points, and reference the data/trends provided.
- **Conclusion:** Summarize the key insights and provide a forward-looking statement.
- **Call to Action:** Encourage professional discussion. "What are your thoughts on these trends? I'm keen to hear from other experts in the comments."

**Image Prompt (Professional Banner):**
- **Style:** "Modern, abstract corporate background, professional banner image".
- **Subject:** Stylized geometric shapes, network nodes, or abstract light patterns that evoke concepts like growth, technology, and connection. No people.
- **Full Prompt Example:** "professional LinkedIn article banner, abstract network of glowing blue and white nodes on a dark navy blue background, sense of digital connection and data flow, clean and modern, no text"

---

### **IF Content Type is `seo_blog_post`:**

**Goal:** Rank on Google for target keywords and provide immense value to the reader.

**SEO Blog Post:**
- **SEO Title:** A keyword-rich title under 60 characters.
- **Meta Description:** An engaging, 155-character summary that includes the main keyword and a call-to-action.
- **Blog Post (H1, H2, H3 Structure):**
    - **(H1) Title:** The main title of the post.
    - **Introduction:** Hook the reader and state what they will learn.
    - **(H2) Section 1:** A deep dive into the first key trend.
    - **(H2) Section 2:** A deep dive into the second key trend.
    - **(H3) Sub-section 2.1:** A more detailed point within section 2.
    - **(H2) Conclusion:** Summarize the key points and provide a final takeaway.
- **Internal Linking Suggestions:** Suggest 2-3 other related topics to link to from within the post.

**Image Prompt (Featured Image):**
- **Style:** "Vibrant, clean illustration, blog post featured image".
- **Subject:** A clear, symbolic representation of the blog post's main topic that is easy to understand at a glance.
- **Full Prompt Example:** "vibrant illustration, a magnifying glass hovering over a bar chart that is trending upwards, surrounded by icons representing marketing and sales, clean and modern vector style, bright color palette"

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

### **IF Content Type is `affiliate_review`:**

Your goal is to build maximum trust and guide the reader to a confident purchase through your link.

**Affiliate Review Content:**
- **Catchy Title:** A title that combines the product name with a powerful benefit or addresses a major question (e.g., "Is [Product Name] Worth It? My Honest 2025 Review").
- **Introduction (The Hook):** Start with a personal story about the problem you faced, which should relate to the identified trends.
- **What is [Product Name] & Who is it For?:** Briefly explain the product and the ideal customer.
- **My Experience & Results (The Core):** Detail your journey with the product. How did it solve your problem? Use the trends as context for why this product is so relevant *right now*.
- **Top 3 Features/Benefits:** Break down the most impactful benefits, linking each one back to solving a specific pain point.
- **What I Didn't Like (The Honesty):** Include 1-2 minor drawbacks or limitations. This builds immense trust and makes your recommendation more believable.
- **The Verdict & Final Recommendation:** A strong summary of why you recommend it despite the minor flaws.
- **Strong Call-to-Action:** A clear, enthusiastic call to action. "Click here to get [Product Name] and see the same results I did. You won't regret it."

**Detailed Image Prompt for Review:**
- **Style:** [e.g., Authentic and candid photography, screen recording GIF, before-and-after graphic]
- **Subject:** You (or a relatable person) genuinely using and enjoying the product. An "unboxing" shot or a screenshot of a key "aha!" moment inside the software.
- **Scene:** A realistic setting, like a home office or a real-world environment where the product would be used.
- **Lighting:** Natural and clean. Avoid looking overly corporate or staged.
- **Mood:** Trustworthy, helpful, authentic, successful.
- **Full Prompt Example:** "candid photo, a man smiling at his laptop screen showing a 'success' graph, a coffee mug next to him, sitting in a cozy, well-lit home office, a feeling of genuine satisfaction and relief, natural light from a window"

**Landing Page Code:**
- **Instructions:** Generate a complete, single HTML file with embedded modern CSS (using the Tailwind CSS CDN for styling) for a high-converting landing page. The page should be clean, professional, and mobile-responsive.
- **Structure:**
    1.  **Hero Section:** A compelling headline based on the review title, a sub-headline explaining the main benefit, and a prominent "Get It Now" CTA button.
    2.  **Problem Section:** A short section with an icon and text describing the pain point the visitor is experiencing (related to the trends).
    3.  **Solution/Benefits Section:** Use 3-5 cards or list items, each with an icon, a benefit headline, and a short description.
    4.  **Social Proof Section:** Include 2-3 placeholder testimonial blocks with a name and a star rating.
    5.  **Final CTA Section:** A final, urgent call-to-action block with another prominent button.
- **Output:** Provide the full, copy-paste-ready HTML code inside a single code block.
        """
        
        trend_str = "\n".join(f"- {t}" for t in trends)
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
            confidence = round(random.uniform(0.88, 0.95), 3)
            
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

# THIS IS THE FINAL, ROBUST analyze_niche ENDPOINT
@api_router.post("/niche/analyze", response_model=TrendAnalysis)
async def analyze_niche(request: NicheRequest):
    try:
        trends = await oracle.monitor_niche_trends(request.niche, request.keywords)
        
        # Handle case where no trends could be found at all
        if not trends:
            return TrendAnalysis(
                niche=request.niche,
                trends=[],
                forecast_summary="Could not fetch any live trend data for this niche. Please try a different or broader niche.",
                top_opportunities=["N/A - Trend data is required for analysis."]
            )

        await db.trends.insert_many([t.dict() for t in trends])

        top_trends_titles = [trend.title for trend in trends[:5]]
        forecast_prompt = f"""As a world-class market analyst, review these top trends in '{request.niche}': {', '.join(top_trends_titles)}. Provide a detailed, actionable forecast (4-6 sentences). Then, identify and rank the **Top 20 most profitable business opportunities** based on these trends. Be specific and creative. Format the opportunities as a numbered list."""
        
        forecast_summary = f"Strong momentum detected in {request.niche}."
        opportunities = [f"Could not generate unique opportunities for {request.niche} at this time."] * 20
        try:
            forecast_response = await oracle.model.generate_content_async(forecast_prompt)
            response_text = forecast_response.text
            parts = response_text.lower().split("top 20 most profitable business opportunities")
            
            if len(parts) > 1:
                forecast_summary = parts[0].strip() or "AI-generated forecast was inconclusive."
                opp_text = parts[1]
                opportunities = [line.split('.', 1)[1].strip() for line in opp_text.split('\n') if line.strip() and line.strip().split('.', 1)[0].isdigit()]
                if not opportunities:
                    opportunities = [line.strip() for line in opp_text.split('\n') if line.strip() and not line.lower().startswith("here are")]
            else:
                forecast_summary = response_text

        except Exception as e:
            logging.warning(f"Forecast generation failed: {e}")
        
        return TrendAnalysis(
            niche=request.niche,
            trends=trends,
            forecast_summary=forecast_summary,
            top_opportunities=opportunities[:20]
        )
    except Exception as e:
        logger.error(f"Critical error in analyze_niche endpoint: {e}")
        raise HTTPException(status_code=500, detail="A critical error occurred during analysis.")

# ... (The rest of your endpoints: generate_content_endpoint, history, stats, etc., and the app configuration remain the same)
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
    history = [doc for doc in await cursor.to_list(length=20)]
    for doc in history:
        doc['_id'] = str(doc['_id'])
    return {"content_history": history}

@api_router.get("/trends/latest/{niche}")
async def get_latest_trends(niche: str):
    cursor = db.trends.find({"niche": niche}).sort("created_at", -1).limit(20)
    trends = [doc for doc in await cursor.to_list(length=20)]
    for doc in trends:
        doc['_id'] = str(doc['_id'])
    return {"trends": trends}
    
    # --- ADD THESE TWO NEW ENDPOINTS TO YOUR server.py FILE ---

@api_router.get("/content/all")
async def get_all_content():
    """Get all generated content pieces, sorted by most recent."""
    try:
        cursor = db.generated_content.find({}).sort("created_at", -1).limit(50)
        all_content = [doc for doc in await cursor.to_list(length=50)]
        for doc in all_content:
            doc['_id'] = str(doc['_id'])
        return {"all_content": all_content}
    except Exception as e:
        logger.error(f"Error fetching all content: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch content history.")

@api_router.get("/trends/all")
async def get_all_trends():
    """Get all monitored trends, sorted by most recent."""
    try:
        cursor = db.trends.find({}).sort("created_at", -1).limit(100)
        all_trends = [doc for doc in await cursor.to_list(length=100)]
        for doc in all_trends:
            doc['_id'] = str(doc['_id'])
        return {"all_trends": all_trends}
    except Exception as e:
        logger.error(f"Error fetching all trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trend history.")

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    try:
        trends_count = await db.trends.count_documents({})
        content_count = await db.generated_content.count_documents({})
        distinct_niches = await db.trends.distinct("niche")
        return {
            "total_trends_monitored": trends_count,
            "content_pieces_generated": content_count,
            "active_niches": distinct_niches or [],
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