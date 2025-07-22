--- START OF FILE backend/server.py ---
import os
import logging
from pathlib import Path

from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional, List

# --- MongoDB Imports ---
from motor.motor_asyncio import AsyncIOMotorClient

# --- IMPORT THE MASTER ENGINE ---
from backend.engine import NicheStackEngine

logger = logging.getLogger(__name__)

# --- CONFIGURATION SETTINGS ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    gemini_api_key: str
    mongo_uri: str
    IP_GEOLOCATION_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

# --- Pydantic Request/Response MODELS ---
class NicheStackRequest(BaseModel):
    interest: str
    product_name: Optional[str] = None
    user_content_text: Optional[str] = None
    user_content_url: Optional[str] = None
    
    user_ip_address: Optional[str] = None
    target_country_name: Optional[str] = None

    # New: Category and Subcategory for more refined searches
    product_category: Optional[str] = None # e.g., "Electronics", "Home & Kitchen", "Fashion"
    product_subcategory: Optional[str] = None # e.g., "Smartphones", "Cookware Sets", "Dresses"

    # Specific fields for Commerce Audit/Social Selling
    user_store_url: Optional[str] = None
    marketplace_link: Optional[str] = None
    product_selling_price: Optional[float] = None
    social_platforms_to_sell: Optional[List[str]] = None
    ads_daily_budget: Optional[float] = None
    number_of_days: Optional[int] = None
    amount_to_buy: Optional[int] = None

    # Specific fields for Arbitrage Finder
    buy_marketplace_link: Optional[str] = None
    sell_marketplace_link: Optional[str] = None

class NicheStackResponse(BaseModel):
    stack: str
    data: Any

# --- FastAPI APP AND ROUTER ---
app = FastAPI(
    title="NicheStack AI",
    description="The AI Co-Pilot for Solopreneurs. This API provides access to the various intelligence stacks.",
    version="1.0.0"
)

api_router = APIRouter(prefix="/api")

db_client: AsyncIOMotorClient = None
database = None
engine: NicheStackEngine = None
app_settings: Settings = None

# --- API HEALTH CHECK ---
@api_router.get("/")
async def root():
    """Provides a simple health check to confirm the API is running."""
    return {"message": "NicheStack AI Backend is operational"}

# --- STACK ENDPOINTS ---
@api_router.post("/idea-stack", response_model=NicheStackResponse, tags=["Stacks"])
async def get_idea_stack(request: NicheStackRequest):
    """
    Runs the Idea Stack to discover and validate new business opportunities
    based on a broad user interest.
    """
    if not engine:
        logger.error("Attempted to call Idea Stack, but AI Engine is not available.")
        raise HTTPException(status_code=503, detail="AI Engine is not available due to missing configuration or failed initialization.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="The 'interest' field cannot be empty for the Idea Stack.")
    
    logger.info(f"Received Idea Stack request for: {request.interest}")
    data = await engine.run_idea_stack(
        request.interest,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,       # New: Pass category
        product_subcategory=request.product_subcategory  # New: Pass subcategory
    )
    
    try:
        if database:
            await database.idea_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Idea Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation for Idea Stack.")
    except Exception as e:
        logger.error(f"Failed to save Idea Stack results to MongoDB: {e}")
    
    return NicheStackResponse(stack="idea", data=data)

@api_router.post("/content-stack", response_model=NicheStackResponse, tags=["Stacks"])
async def get_content_stack(request: NicheStackRequest):
    """
    Runs the Content Stack to generate a base package of content ideas
    for a given niche or interest.
    """
    if not engine:
        logger.error("Attempted to call Content Stack, but AI Engine is not available.")
        raise HTTPException(status_code=503, detail="AI Engine is not available due to missing configuration or failed initialization.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="The 'interest' field cannot be empty for the Content Stack.")
    
    logger.info(f"Received Content Stack request for: {request.interest}")
    data = await engine.run_content_stack(
        request.interest,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory
    )
    
    try:
        if database:
            await database.content_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Content Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation for Content Stack.")
    except Exception as e:
        logger.error(f"Failed to save Content Stack results to MongoDB: {e}")

    return NicheStackResponse(stack="content", data=data)

@api_router.post("/commerce-stack", response_model=NicheStackResponse, tags=["Stacks"])
async def get_commerce_stack(request: NicheStackRequest):
    """
    Runs the Commerce Stack to perform market analysis on a specific product.
    """
    if not engine:
        logger.error("Attempted to call Commerce Stack, but AI Engine is not available.")
        raise HTTPException(status_code=503, detail="AI Engine is not available due to missing configuration or failed initialization.")
    if not request.product_name:
        raise HTTPException(status_code=400, detail="The 'product_name' field is required for the Commerce Stack.")
        
    logger.info(f"Received Commerce Stack request for: {request.product_name}")
    data = await engine.run_commerce_stack(
        product_name=request.product_name,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory,
        user_store_url=request.user_store_url,
        marketplace_link=request.marketplace_link,
        product_selling_price=request.product_selling_price,
        social_platforms_to_sell=request.social_platforms_to_sell,
        ads_daily_budget=request.ads_daily_budget,
        number_of_days=request.number_of_days,
        amount_to_buy=request.amount_to_buy
    )

    try:
        if database:
            await database.commerce_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Commerce Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation for Commerce Stack.")
    except Exception as e:
        logger.error(f"Failed to save Commerce Stack results to MongoDB: {e}")

    return NicheStackResponse(stack="commerce", data=data)

@api_router.post("/strategy-stack", response_model=NicheStackResponse, tags=["Stacks"])
async def get_strategy_stack(request: NicheStackRequest):
    """
    Runs the Strategy Stack to generate a comprehensive SEO and keyword strategy
    for a given niche or interest.
    """
    if not engine:
        logger.error("Attempted to call Strategy Stack, but AI Engine is not available.")
        raise HTTPException(status_code=503, detail="AI Engine is not available due to missing configuration or failed initialization.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="The 'interest' field is required for the Strategy Stack.")
        
    logger.info(f"Received Strategy Stack request for: {request.interest}")
    data = await engine.run_strategy_stack(
        request.interest,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory
    )

    try:
        if database:
            await database.strategy_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Strategy Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation for Strategy Stack.")
    except Exception as e:
        logger.error(f"Failed to save Strategy Stack results to MongoDB: {e}")

    return NicheStackResponse(stack="strategy", data=data)

@api_router.post("/arbitrage-stack", response_model=NicheStackResponse, tags=["Stacks"])
async def get_arbitrage_stack(request: NicheStackRequest):
    """
    Runs the Arbitrage Finder Stack to identify buy-low, sell-high opportunities.
    Requires product_name, buy_marketplace_link, and sell_marketplace_link.
    """
    if not engine:
        logger.error("Attempted to call Arbitrage Stack, but AI Engine is not available.")
        raise HTTPException(status_code=503, detail="AI Engine is not available due to missing configuration or failed initialization.")
    if not all([request.product_name, request.buy_marketplace_link, request.sell_marketplace_link]):
        raise HTTPException(status_code=400, detail="For Arbitrage Stack, 'product_name', 'buy_marketplace_link', and 'sell_marketplace_link' are required.")
    
    logger.info(f"Received Arbitrage Stack request for product: '{request.product_name}'")

    # Import the PriceArbitrageFinder here to avoid circular dependencies
    from backend.price_arbitrage_finder import PriceArbitrageFinder

    finder = PriceArbitrageFinder(gemini_api_key=app_settings.gemini_api_key)
    
    data = await finder.find_arbitrage_opportunities(
        product_name=request.product_name,
        buy_marketplace_link=request.buy_marketplace_link,
        sell_marketplace_link=request.sell_marketplace_link,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,      # New: Pass category
        product_subcategory=request.product_subcategory # New: Pass subcategory
    )

    try:
        if database:
            await database.arbitrage_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Arbitrage Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation for Arbitrage Stack.")
    except Exception as e:
        logger.error(f"Failed to save Arbitrage Stack results to MongoDB: {e}")

    return NicheStackResponse(stack="arbitrage", data=data)

@api_router.post("/social-selling-stack", response_model=NicheStackResponse, tags=["Stacks"])
async def get_social_selling_stack(request: NicheStackRequest):
    """
    Runs the Social Selling Strategist Stack to analyze profitability and suggest strategies.
    Requires product_name, product_selling_price, social_platforms_to_sell, ads_daily_budget,
    number_of_days, and amount_to_buy.
    """
    if not engine:
        logger.error("Attempted to call Social Selling Stack, but AI Engine is not available.")
        raise HTTPException(status_code=503, detail="AI Engine is not available due to missing configuration or failed initialization.")
    if not all([request.product_name, request.product_selling_price is not None, 
                request.social_platforms_to_sell, request.ads_daily_budget is not None, 
                request.number_of_days is not None, request.amount_to_buy is not None]):
        raise HTTPException(status_code=400, detail="For Social Selling Stack, 'product_name', 'product_selling_price', 'social_platforms_to_sell', 'ads_daily_budget', 'number_of_days', and 'amount_to_buy' are required.")

    logger.info(f"Received Social Selling Stack request for product: '{request.product_name}'")

    # Import the SocialSellingStrategist here to avoid circular dependencies
    from backend.social_selling_strategist import SocialSellingStrategist

    strategist = SocialSellingStrategist(gemini_api_key=app_settings.gemini_api_key)

    data = await strategist.analyze_social_selling(
        product_name=request.product_name,
        product_selling_price=request.product_selling_price,
        social_platforms_to_sell=request.social_platforms_to_sell,
        ads_daily_budget=request.ads_daily_budget,
        number_of_days=request.number_of_days,
        amount_to_buy=request.amount_to_buy,
        supplier_marketplace_link=request.marketplace_link,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory
    )

    try:
        if database:
            await database.social_selling_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Social Selling Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation for Social Selling Stack.")
    except Exception as e:
        logger.error(f"Failed to save Social Selling Stack results to MongoDB: {e}")

    return NicheStackResponse(stack="social_selling", data=data)

@api_router.post("/product-route-stack", response_model=NicheStackResponse, tags=["Stacks"])
async def get_product_route_stack(request: NicheStackRequest):
    """
    Runs the Product Route Suggester Stack to suggest trending products and optimal routes.
    Requires niche_interest.
    """
    if not engine:
        logger.error("Attempted to call Product Route Stack, but AI Engine is not available.")
        raise HTTPException(status_code=503, detail="AI Engine is not available due to missing configuration or failed initialization.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="The 'interest' field is required for the Product Route Suggester Stack.")

    logger.info(f"Received Product Route Suggester Stack request for niche: '{request.interest}'")

    # Import the ProductRouteSuggester here to avoid circular dependencies
    from backend.product_route_suggester import ProductRouteSuggester

    suggester = ProductRouteSuggester(gemini_api_key=app_settings.gemini_api_key)

    data = await suggester.suggest_product_and_route(
        niche_interest=request.interest,
        user_content_text=request.user_content_text,
        user_content_url=request.user_content_url,
        user_ip_address=request.user_ip_address,
        target_country_name=request.target_country_name,
        product_category=request.product_category,
        product_subcategory=request.product_subcategory
    )

    try:
        if database:
            await database.product_route_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Product Route Suggester Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation for Product Route Suggester Stack.")
    except Exception as e:
        logger.error(f"Failed to save Product Route Suggester Stack results to MongoDB: {e}")

    return NicheStackResponse(stack="product_route", data=data)


# --- Final App Configuration ---
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MongoDB Connection Events ---
@app.on_event("startup")
async def startup_event():
    """
    Connects to MongoDB and initializes the NicheStackEngine when the FastAPI app starts.
    """
    global db_client, database, engine, app_settings

    try:
        app_settings = Settings()
        logger.info("Application settings loaded.")
    except Exception as e:
        logger.critical(f"FATAL: Failed to load application settings (environment variables). Please ensure .env is configured correctly: {e}")
        app_settings = None


    if app_settings and app_settings.mongo_uri:
        try:
            db_client = AsyncIOMotorClient(app_settings.mongo_uri)
            database = db_client.get_database("nichestack_db")
            await database.command("ping")
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.critical(f"Failed to connect to MongoDB with URI '{app_settings.mongo_uri}': {e}. Database functionality will be unavailable.")
            db_client = None
            database = None
    else:
        logger.warning("MONGO_URI not set or settings failed to load. Database connection skipped.")
        db_client = None
        database = None

    if app_settings and app_settings.gemini_api_key:
        try:
            engine = NicheStackEngine(
                gemini_api_key=app_settings.gemini_api_key,
                ip_geolocation_api_key=app_settings.IP_GEOLOCATION_API_KEY
            )
            logger.info("NicheStack AI Engine initialized.")
        except Exception as e:
            logger.critical(f"Failed to initialize NicheStack AI Engine: {e}. AI functionalities will be unavailable.")
            engine = None
    else:
        logger.warning("GEMINI_API_KEY not set or settings failed to load. AI Engine will not be available.")
        engine = None


@app.on_event("shutdown")
async def shutdown_event():
    """
    Closes the MongoDB connection when the FastAPI app shuts down.
    """
    global db_client
    if db_client:
        db_client.close()
        logger.info("MongoDB connection closed.")
--- END OF FILE backend/server.py ---