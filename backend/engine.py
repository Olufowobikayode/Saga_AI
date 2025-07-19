# file: backend/engine.py

import asyncio
import logging
import json
from typing import Dict, Any

import google.generativeai as genai

# --- IMPORT ALL SPECIALIST ENGINES AND SCRAPERS ---
# Each of these is a dedicated module responsible for a specific data-gathering task.
from q_and_a import UniversalScraper
from trends import TrendScraper
from scraper import WebScraper
from keyword_engine import KeywordEngine as GoogleApiEngine # Rename for clarity

logger = logging.getLogger(__name__)

class NicheStackEngine:
    """
    The central engine and "heart" of the NicheStack AI application.
    This class orchestrates all specialist modules to execute the logic for each
    of the platform's "Stacks". It acts as a facade, providing a simple interface
    to a complex underlying data-gathering and synthesis system.
    """
    def __init__(self, gemini_api_key: str):
        """
        Initializes the AI model and creates a single, persistent instance of
        each specialist data-gathering engine. This is done once when the server
        starts for maximum efficiency.
        """
        logger.info("Initializing NicheStackEngine and all specialist modules...")
        
        # Initialize the primary AI Model
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

        # Initialize all specialist engines
        self.q_and_a_scraper = UniversalScraper()
        self.trend_tool_scraper = TrendScraper()
        self.general_scraper = WebScraper()
        self.google_engine = GoogleApiEngine() # Specialist for Google services
        
        logger.info("NicheStackEngine initialized successfully.")

    async def _generate_json_response(self, prompt: str) -> Dict:
        """A centralized helper to get a structured JSON response from the AI model."""
        try:
            response = await self.model.generate_content_async(prompt)
            json_str = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to generate or parse AI JSON response: {e}")
            return {"error": "AI generation or parsing failed.", "details": str(e)}

    # --- STACK 1: IDEA STACK LOGIC ---
    async def run_idea_stack(self, interest: str) -> Dict:
        """
        Orchestrates the full data pipeline for the Idea Stack. It calls upon
        multiple specialist engines in parallel to gather a wide range of data.
        """
        logger.info(f"Running Idea Stack for interest: '{interest}'")
        
        # Step 1: Define and run all data gathering tasks in parallel.
        # This demonstrates the power of the facade, calling each specialist.
        google_trends_task = self.google_engine.get_google_trends_data(interest)
        community_task = self.q_and_a_scraper.run_scraping_tasks(interest)
        keyword_tool_task = self.trend_tool_scraper.run_scraper_tasks(interest)

        # Run all tasks concurrently and wait for their results
        results = await asyncio.gather(
            google_trends_task,
            community_task,
            keyword_tool_task,
            return_exceptions=True
        )
        
        # Unpack results for clarity
        google_data = results[0]
        community_data = results[1]
        keyword_tool_data = results[2]

        # Step 2: Create a sophisticated prompt for the AI to synthesize all gathered data.
        prompt = f"""
        Act as a seasoned venture capitalist and market analyst. You have been presented with the following comprehensive, multi-source market intelligence report for the niche '{interest}':
        
        --- PILLAR 1: GOOGLE SEARCH & TREND DATA ---
        {json.dumps(google_data, indent=2)}

        --- PILLAR 2: COMMUNITY & Q&A PLATFORM INSIGHTS (The Voice of the Customer) ---
        {json.dumps(community_data, indent=2)}
        
        --- PILLAR 3: KEYWORD TOOL SUGGESTIONS ---
        {json.dumps(keyword_tool_data, indent=2)}
        --- END REPORT ---

        **Your Task:**
        Synthesize all of this raw data. Your goal is to identify deep market needs and gaps. Generate a ranked list of the **Top 5 most innovative and commercially viable business ideas**.

        For each idea, provide:
        1. "title": A compelling name for the business.
        2. "description": A one-sentence pitch explaining the core problem it solves, referencing the data.
        3. "confidence_score": Your confidence (as a percentage, e.g., "95%") that this is a real, data-backed market need.
        
        Format your final output as a valid JSON array of objects.
        """
        
        # Step 3: Generate the final strategic output.
        return await self._generate_json_response(prompt)

    # --- PLACEHOLDERS FOR OTHER STACKS ---
    # Each of these would follow the same pattern: call the necessary specialist engines,
    # gather the data, and then pass it to the AI for synthesis.
    async def run_content_stack(self, interest: str) -> Dict:
        logger.info(f"Running Content Stack for interest: '{interest}'")
        # Example: Could use the google_engine and trend_scraper for content topics
        return {"placeholder": f"Content package for {interest} would be generated here."}

    async def run_commerce_stack(self, product_name: str) -> Dict:
        logger.info(f"Running Commerce Stack for product: '{product_name}'")
        # Example: Could use the general WebScraper from scraper.py to scrape Jumia/Konga
        return {"placeholder": f"E-commerce analysis for {product_name} would be generated here."}

    async def run_strategy_stack(self, interest: str) -> Dict:
        logger.info(f"Running Strategy Stack for interest: '{interest}'")
        # Example: This stack would likely use all engines to create a full SEO strategy
        return {"placeholder": f"SEO strategy for {interest} would be generated here."}