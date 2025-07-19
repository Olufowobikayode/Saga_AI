from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict
import uuid
from datetime import datetime, timezone
import asyncio
import google.generativeai as genai
import certifi
from pytrends.request import TrendReq

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- INITIAL SETUP & CONFIG ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- DATABASE & API CLIENTS ---
try:
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    gemini_api_key = os.environ['GEMINI_API_KEY']
    ca = certifi.where()
    client = AsyncIOMotorClient(mongo_url, tlsCAFile=ca)
    db = client[db_name]
    genai.configure(api_key=gemini_api_key)
except KeyError as e:
    logger.error(f"FATAL: Environment variable {e} not set.")
    raise

# --- Pydantic MODELS ---
class IdeaRequest(BaseModel):
    interest: str

class BusinessIdea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    data_sources: List[str]

# --- NicheStack AI Core Engine ---
class NicheStackEngine:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def _get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    async def _run_in_executor(self, sync_func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, sync_func, *args)

    async def get_google_trends_data(self, interest: str) -> List[str]:
        logger.info(f"Fetching Google Trends data for '{interest}'...")
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            await self._run_in_executor(pytrends.build_payload, [interest], cat=0, timeframe='today 12-m', geo='', gprop='')
            related_queries = await self._run_in_executor(pytrends.related_queries)
            top_queries = related_queries[interest].get('top')
            if top_queries is not None:
                return top_queries['query'].tolist()[:5]
        except Exception as e:
            logger.error(f"Failed to fetch Google Trends data: {e}")
        return []

    async def scrape_q_and_a_site(self, site: str, interest: str) -> List[str]:
        driver = self._get_driver()
        results = []
        try:
            logger.info(f"Scraping {site} for pain points related to '{interest}'...")
            search_query = f'"{interest}" problem OR "how to" OR struggle'
            if site == "Reddit":
                driver.get(f"https://www.reddit.com/search/?q={search_query}&type=comment")
                wait_selector = '[data-testid="comment"]'
            elif site == "Quora":
                driver.get(f"https://www.quora.com/search?q={search_query}")
                wait_selector = '.qu-userText'
            
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, wait_selector)))
            elements = driver.find_elements(By.CSS_SELECTOR, wait_selector)
            results = [el.text for el in elements[:3]] # Get top 3 results
            logger.info(f"Found {len(results)} potential pain points from {site}.")
        except Exception as e:
            logger.error(f"Failed to scrape {site}: {e}")
        finally:
            driver.quit()
        return results

    async def find_business_ideas(self, interest: str) -> List[BusinessIdea]:
        tasks = [
            self.get_google_trends_data(interest),
            self.scrape_q_and_a_site("Reddit", interest),
            self.scrape_q_and_a_site("Quora", interest)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        google_trends_data, reddit_pain_points, quora_pain_points = results

        if isinstance(google_trends_data, Exception): google_trends_data = []
        if isinstance(reddit_pain_points, Exception): reddit_pain_points = []
        if isinstance(quora_pain_points, Exception): quora_pain_points = []
        
        if not (google_trends_data or reddit_pain_points or quora_pain_points):
            return [BusinessIdea(title="Insufficient Data", description="Could not find sufficient data to generate ideas. Please try a broader interest.", data_sources=["Initial Check"])]

        prompt = f"""
        As a business strategist, analyze the following market data for the niche '{interest}':
        - Google Trends Breakout Queries: {google_trends_data}
        - Reddit User Pain Points: {reddit_pain_points}
        - Quora User Questions: {quora_pain_points}

        Synthesize this data to generate 5 innovative business ideas. For each idea, provide a compelling title and a one-sentence description explaining how it addresses the gathered data.
        Format the output as a valid JSON array of objects with "title" and "description" keys.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            ideas_json_str = response.text.strip().replace('```json', '').replace('```', '')
            ideas_data = json.loads(ideas_json_str)
            
            return [
                BusinessIdea(title=idea['title'], description=idea['description'], data_sources=["Google Trends", "Reddit", "Quora"])
                for idea in ideas_data
            ]
        except Exception as e:
            logger.error(f"Failed to generate business ideas with AI: {e}")
            return [BusinessIdea(title="AI Generation Error", description=f"The AI failed to process the scraped data. Details: {str(e)}", data_sources=["Gemini AI"])]

# --- FastAPI APP AND ROUTER ---
app = FastAPI(title="NicheStack AI", description="The AI Co-Pilot for Solopreneurs")
api_router = APIRouter(prefix="/api")
engine = NicheStackEngine()

@api_router.get("/")
async def root():
    return {"message": "NicheStack AI Backend is operational"}

# --- STACK 1: IDEA STACK ---
@api_router.post("/idea-stack/generate-ideas", response_model=List[BusinessIdea])
async def generate_niche_ideas(request: IdeaRequest):
    if not request.interest:
        raise HTTPException(status_code=400, detail="Interest cannot be empty.")
    return await engine.find_business_ideas(request.interest)

# --- PLACEHOLDER ENDPOINTS FOR OTHER STACKS (returning structured mock data) ---
@api_router.get("/content-stack/generate-base-post")
async def generate_base_post():
    await asyncio.sleep(1) # Simulate work
    return {
        "catchy_post": "🚀 5 AI Tools That Will 10x Your Productivity This Week...",
        "image_prompt": "cinematic photo, a stressed entrepreneur suddenly looking relieved and empowered while looking at their laptop screen showing a clean dashboard, mood is inspiring and problem-solving, 4k"
    }

@api_router.get("/commerce-stack/get-products")
async def get_commerce_products():
    await asyncio.sleep(1)
    return {
        "pod_ideas": [{"title": "Minimalist 'Code & Coffee' T-Shirt"}, {"title": "Funny 'Crypto HODL' Mug"}],
        "ecommerce_products": [{"name": "Smart Water Bottle", "price": "~$15"}, {"name": "Portable Neck Fan", "price": "~$8"}]
    }

app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])