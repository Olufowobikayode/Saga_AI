# file: backend/server.py

import os
import logging
from pathlib import Path

from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Optional # Added Optional

# --- MongoDB Imports ---
from motor.motor_asyncio import AsyncIOMotorClient

# --- IMPORT THE MASTER ENGINE ---
# This is the single point of contact for all application logic.
from engine import NicheStackEngine

# --- INITIAL SETUP & CONFIG ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Pydantic Request/Response MODELS ---
# These define the data structure for our API.
class NicheStackRequest(BaseModel):
    interest: str
    product_name: Optional[str] = None # Optional, for Commerce Stack
    user_content_text: Optional[str] = None # New: Optional field for direct text input
    user_content_url: Optional[str] = None  # New: Optional field for URL input
    # Add other potential inputs here as stacks evolve, e.g., blog_url: str = None

class NicheStackResponse(BaseModel):
    stack: str
    data: Any

# --- FastAPI APP AND ROUTER ---
app = FastAPI(
    title="NicheStack AI",
    description="The AI Co-Pilot for Solopreneurs. This API provides access to the various intelligence stacks.",
    version="1.0.0"
)

api_router = APOUTER(prefix="/api") # Corrected typo: APIRouter

# Global variable for MongoDB client and database (initialized in startup event)
db_client: AsyncIOMotorClient = None
database = None
engine: NicheStackEngine = None # Initialize engine as None globally

# --- API HEALTH CHECK ---
@api_router.get("/")
async def root():
    """Provides a simple health check to confirm the API is running."""
    return {"message": "NicheStack AI Backend is operational"}

# --- STACK ENDPOINTS ---
# Each endpoint is a clean, simple interface to a complex backend process.

@api_router.post("/idea-stack", response_model=NicheStackResponse, tags=["Stacks"])
async def get_idea_stack(request: NicheStackRequest):
    """
    Runs the Idea Stack to discover and validate new business opportunities
    based on a broad user interest.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="AI Engine is not available due to missing configuration.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="The 'interest' field cannot be empty for the Idea Stack.")
    
    logger.info(f"Received Idea Stack request for: {request.interest}")
    data = await engine.run_idea_stack(
        request.interest,
        user_content_text=request.user_content_text, # Passed new field
        user_content_url=request.user_content_url   # Passed new field
    )
    
    # Optional: Save the results to your MongoDB database here
    try:
        if database: # Ensure database connection is active
            await database.idea_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Idea Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation.")
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
        raise HTTPException(status_code=503, detail="AI Engine is not available.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="The 'interest' field cannot be empty for the Content Stack.")
    
    logger.info(f"Received Content Stack request for: {request.interest}")
    data = await engine.run_content_stack(
        request.interest,
        user_content_text=request.user_content_text, # Passed new field
        user_content_url=request.user_content_url   # Passed new field
    )
    
    # Optional: Save the results to your MongoDB database here
    try:
        if database:
            await database.content_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Content Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation.")
    except Exception as e:
        logger.error(f"Failed to save Content Stack results to MongoDB: {e}")

    return NicheStackResponse(stack="content", data=data)

@api_router.post("/commerce-stack", response_model=NicheStackResponse, tags=["Stacks"])
async def get_commerce_stack(request: NicheStackRequest):
    """
    Runs the Commerce Stack to perform market analysis on a specific product.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="AI Engine is not available.")
    if not request.product_name:
        raise HTTPException(status_code=400, detail="The 'product_name' field is required for the Commerce Stack.")
        
    logger.info(f"Received Commerce Stack request for: {request.product_name}")
    data = await engine.run_commerce_stack(
        request.product_name,
        user_content_text=request.user_content_text, # Passed new field
        user_content_url=request.user_content_url   # Passed new field
    )

    # Optional: Save the results to your MongoDB database here
    try:
        if database:
            await database.commerce_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Commerce Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation.")
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
        raise HTTPException(status_code=503, detail="AI Engine is not available.")
    if not request.interest:
        raise HTTPException(status_code=400, detail="The 'interest' field is required for the Strategy Stack.")
        
    logger.info(f"Received Strategy Stack request for: {request.interest}")
    data = await engine.run_strategy_stack(
        request.interest,
        user_content_text=request.user_content_text, # Passed new field
        user_content_url=request.user_content_url   # Passed new field
    )

    # Optional: Save the results to your MongoDB database here
    try:
        if database:
            await database.strategy_results.insert_one({"request": request.dict(), "response": data})
            logger.info("Strategy Stack results saved to MongoDB.")
        else:
            logger.warning("MongoDB database not connected. Skipping save operation.")
    except Exception as e:
        logger.error(f"Failed to save Strategy Stack results to MongoDB: {e}")

    return NicheStackResponse(stack="strategy", data=data)

# --- Final App Configuration ---
app.include_router(api_router)

# Configure CORS (Cross-Origin Resource Sharing) to allow your frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you should restrict this to your frontend's domain
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
    global db_client, database, engine

    # 1. Initialize MongoDB Connection
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        logger.error("FATAL: MONGO_URI environment variable is not set. Database connection skipped.")
        db_client = None
        database = None
    else:
        try:
            db_client = AsyncIOMotorClient(mongo_uri)
            database = db_client.get_database("nichestack_db") # Or your chosen database name
            # Optional: Ping the database to ensure connection
            await database.command("ping")
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            db_client = None
            database = None # Ensure database is None if connection fails

    # 2. Initialize the NicheStackEngine
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_api_key:
        logger.error("FATAL: GEMINI_API_KEY environment variable is not set. AI Engine will not be available.")
        engine = None
    else:
        try:
            engine = NicheStackEngine(gemini_api_key=gemini_api_key)
            logger.info("NicheStack AI Engine initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize NicheStack AI Engine: {e}")
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