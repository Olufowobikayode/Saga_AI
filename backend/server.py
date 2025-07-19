# file: backend/server.py

import os
import logging
from pathlib import Path

from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

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
    product_name: str = None # Optional, for Commerce Stack
    # Add other potential inputs here as stacks evolve, e.g., blog_url: str = None

class NicheStackResponse(BaseModel):
    stack: str
    data: Any

# --- INITIALIZE THE MASTER ENGINE ---
# This single line creates an instance of your entire application's logic.
# It reads the API key and initializes all underlying scrapers and AI models.
gemini_api_key = os.environ.get('GEMINI_API_KEY')
if not gemini_api_key:
    logger.error("FATAL: GEMINI_API_KEY environment variable is not set. The engine cannot start.")
    # Set engine to None so we can handle this gracefully in the API calls.
    engine = None
else:
    engine = NicheStackEngine(gemini_api_key=gemini_api_key)

# --- FastAPI APP AND ROUTER ---
app = FastAPI(
    title="NicheStack AI",
    description="The AI Co-Pilot for Solopreneurs. This API provides access to the various intelligence stacks.",
    version="1.0.0"
)

api_router = APIRouter(prefix="/api")

# --- API HEALTH CHECK ---
@api_router.get("/")
async def root():
    """Provides a simple health check to confirm the API is running."""
    return {"message": "NicheStack AI Backend is operational"}

# --- STACK ENDPOINTS ---
# Each endpoint is a clean, simple interface to a complex backend process.

@api_outer.post("/idea-stack", response_model=NicheStackResponse, tags=["Stacks"])
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
    data = await engine.run_idea_stack(request.interest)
    
    # Optional: Save the results to your MongoDB database here
    # await db.idea_results.insert_one({"request": request.dict(), "response": data})
    
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
    data = await engine.run_content_stack(request.interest)
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
    data = await engine.run_commerce_stack(request.product_name)
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
    data = await engine.run_strategy_stack(request.interest)
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

# You can add startup/shutdown events here if needed, for things like connecting to a database
# @app.on_event("startup")
# async def startup_event():
#     # This is where you would traditionally connect to your MongoDB client
#     pass