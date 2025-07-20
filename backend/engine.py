# file: backend/engine.py

import asyncio
import logging
import json
from typing import Dict, Any, Optional # Added Optional
import aiohttp # Added for fetching URL content

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
        self.general_scraper = WebScraper() # Note: This can be used for general purpose URL scraping if needed
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

    async def _fetch_url_content(self, url: str) -> Optional[str]:
        """Fetches text content from a URL using aiohttp."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
                    text = await response.text()
                    # A very basic way to get "main" content. For more advanced parsing
                    # (e.g., extracting just article body), you'd integrate BeautifulSoup here.
                    # For now, we return a truncated portion to save on token usage and avoid irrelevant parts.
                    return text[:8000] # Return first 8KB of text as a sample
        except aiohttp.ClientError as e:
            logger.warning(f"Failed to fetch content from URL {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching URL {url}: {e}")
            return None

    # --- STACK 1: IDEA STACK LOGIC ---
    async def run_idea_stack(self, interest: str, 
                             user_content_text: Optional[str] = None, 
                             user_content_url: Optional[str] = None) -> Dict:
        """
        Orchestrates the full data pipeline for the Idea Stack. It calls upon
        multiple specialist engines in parallel to gather a wide range of data.
        """
        logger.info(f"Running Idea Stack for interest: '{interest}'")
        
        # Step 1: Define and run all data gathering tasks in parallel.
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

        # Step 2: Prepare user tone instruction
        user_tone_instruction = ""
        user_input_content_for_ai = None

        if user_content_text:
            user_input_content_for_ai = user_content_text
            logger.info("Using provided user content text for tone analysis.")
        elif user_content_url:
            scraped_content = await self._fetch_url_content(user_content_url)
            if scraped_content:
                user_input_content_for_ai = scraped_content
                logger.info(f"Using scraped content from URL {user_content_url} for tone analysis.")
            else:
                logger.warning(f"Could not fetch content from URL: {user_content_url}. Skipping tone analysis from URL.")
        
        if user_input_content_for_ai:
            user_tone_instruction = f"""
            **USER'S WRITING STYLE REFERENCE:**
            Below is content provided by the user. Carefully analyze its tone, style, vocabulary, sentence structure, and overall communication approach. When generating your response, mimic this writing style to make the output sound more personal, human, and aligned with the user's voice. Pay attention to formality, enthusiasm, directness, and any specific quirks.
            ---
            {user_input_content_for_ai}
            ---
            """
        else:
            logger.info("No user content provided for tone analysis. Using default AI tone.")

        # Step 3: Create a sophisticated prompt for the AI to synthesize all gathered data.
        prompt = f"""
        Act as a seasoned venture capitalist and market analyst. You have been presented with the following comprehensive, multi-source market intelligence report for the niche '{interest}':
        
        --- PILLAR 1: GOOGLE SEARCH & TREND DATA ---
        {json.dumps(google_data, indent=2)}

        --- PILLAR 2: COMMUNITY & Q&A PLATFORM INSIGHTS (The Voice of the Customer) ---
        {json.dumps(community_data, indent=2)}
        
        --- PILLAR 3: KEYWORD TOOL SUGGESTIONS ---
        {json.dumps(keyword_tool_data, indent=2)}
        --- END REPORT ---

        {user_tone_instruction} # <--- Inject the tone instruction here

        **Your Task:**
        Synthesize all of this raw data. Your goal is to identify deep market needs and gaps. Generate a ranked list of the **Top 5 most innovative and commercially viable business ideas**.

        For each idea, provide:
        1. "title": A compelling name for the business.
        2. "description": A one-sentence pitch explaining the core problem it solves, referencing the data.
        3. "confidence_score": Your confidence (as a percentage, e.g., "95%") that this is a real, data-backed market need.
        
        Format your final output as a valid JSON array of objects.
        """
        
        # Step 4: Generate the final strategic output.
        return await self._generate_json_response(prompt)

    # --- PLACEHOLDERS FOR OTHER STACKS ---
    # Each of these would follow the same pattern: call the necessary specialist engines,
    # gather the data, and then pass it to the AI for synthesis, incorporating tone.
    async def run_content_stack(self, interest: str, 
                                  user_content_text: Optional[str] = None, 
                                  user_content_url: Optional[str] = None) -> Dict:
        logger.info(f"Running Content Stack for interest: '{interest}'")
        # Example: Could use the google_engine and trend_scraper for content topics
        
        user_tone_instruction = ""
        user_input_content_for_ai = None

        if user_content_text:
            user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self._fetch_url_content(user_content_url)
            if scraped_content:
                user_input_content_for_ai = scraped_content
        
        if user_input_content_for_ai:
            user_tone_instruction = f"""
            **USER'S WRITING STYLE REFERENCE:**
            ---
            {user_input_content_for_ai}
            ---
            Generate the content for the user, mimicking the tone, style, and vocabulary found in the above reference content.
            """

        prompt = f"""
        You are an expert content strategist. Based on the interest '{interest}', generate 5 compelling blog post titles and a short, engaging description for each.
        {user_tone_instruction}
        Format your output as a JSON array of objects, each with "title" and "description" keys.
        """
        return await self._generate_json_response(prompt)


    async def run_commerce_stack(self, product_name: str, 
                                 user_content_text: Optional[str] = None, 
                                 user_content_url: Optional[str] = None) -> Dict:
        logger.info(f"Running Commerce Stack for product: '{product_name}'")
        # Example: Could use the general WebScraper from scraper.py to scrape Jumia/Konga
        user_tone_instruction = ""
        user_input_content_for_ai = None

        if user_content_text:
            user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self._fetch_url_content(user_content_url)
            if scraped_content:
                user_input_content_for_ai = scraped_content
        
        if user_input_content_for_ai:
            user_tone_instruction = f"""
            **USER'S WRITING STYLE REFERENCE:**
            ---
            {user_input_content_for_ai}
            ---
            When generating your analysis, adopt the tone and style present in the user's provided content.
            """

        # This is a placeholder, you'd integrate actual scraping/API calls here
        # Example: product_data = await self.general_scraper.scrape_multiple_sites(product_name, ["Jumia"])
        product_analysis_data = {"product": product_name, "market_sentiment": "Placeholder analysis data."}

        prompt = f"""
        You are an e-commerce market analyst. Analyze the product '{product_name}' using the following data:
        {json.dumps(product_analysis_data, indent=2)}
        {user_tone_instruction}
        Provide a brief market overview, potential challenges, and key selling points for this product.
        Format your output as a JSON object with keys like "overview", "challenges", "selling_points".
        """
        return await self._generate_json_response(prompt)

    async def run_strategy_stack(self, interest: str, 
                                 user_content_text: Optional[str] = None, 
                                 user_content_url: Optional[str] = None) -> Dict:
        logger.info(f"Running Strategy Stack for interest: '{interest}'")
        # Example: This stack would likely use all engines to create a full SEO strategy
        user_tone_instruction = ""
        user_input_content_for_ai = None

        if user_content_text:
            user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self._fetch_url_content(user_content_url)
            if scraped_content:
                user_input_content_for_ai = scraped_content
        
        if user_input_content_for_ai:
            user_tone_instruction = f"""
            **USER'S WRITING STYLE REFERENCE:**
            ---
            {user_input_content_for_ai}
            ---
            When outlining the strategy, ensure the language and presentation style match the user's provided content.
            """

        # Placeholder for data gathering relevant to strategy
        seo_data = {
            "top_keywords": ["example keyword 1", "example keyword 2"],
            "competitor_analysis": "Placeholder competitor insights."
        }
        
        prompt = f"""
        You are a seasoned SEO and digital marketing strategist. Based on the interest '{interest}' and the following data:
        {json.dumps(seo_data, indent=2)}
        {user_tone_instruction}
        Outline a high-level SEO and content strategy. Include sections for "keyword_focus", "content_pillars", and "promotion_channels".
        Format your output as a JSON object.
        """
        return await self._generate_json_response(prompt)