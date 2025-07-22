--- START OF FILE backend/engine.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional
import aiohttp # Added for fetching URL content

import google.generativeai as genai

# --- IMPORT ALL SPECIALIST ENGINES AND SCRAPERS ---
# Each of these is a dedicated module responsible for a specific data-gathering task.
from backend.q_and_a import UniversalScraper
from backend.trends import TrendScraper
from backend.scraper import WebScraper
from backend.keyword_engine import KeywordEngine as GoogleApiEngine # Rename for clarity
from backend.global_ecommerce_scraper import GlobalEcommerceScraper # Import for tone analysis and specific commerce needs

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
        self.global_ecommerce_scraper = GlobalEcommerceScraper() # Used for user content and general commerce scrapes
        
        logger.info("NicheStackEngine initialized successfully.")

    async def _generate_json_response(self, prompt: str) -> Dict:
        """A centralized helper to get a structured JSON response from the AI model."""
        try:
            response = await self.model.generate_content_async(prompt)
            json_str = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"AI response was not valid JSON: {json_str[:500]}... Error: {e}")
            return {"error": "AI response parsing failed: Invalid JSON.", "details": str(e), "raw_response_snippet": json_str[:500]}
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return {"error": "AI generation failed.", "details": str(e)}

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        """Helper to generate AI instruction for mimicking user tone by fetching and processing user content."""
        user_input_content_for_ai = None
        if user_content_text:
            user_input_content_for_ai = user_content_text
            logger.info("Using provided user content text for tone analysis.")
        elif user_content_url:
            # Use the global_ecommerce_scraper's method, which handles aiohttp/selenium fallback
            scraped_content = await self.global_ecommerce_scraper.get_user_store_content(user_content_url)
            if scraped_content:
                user_input_content_for_ai = scraped_content
                logger.info(f"Using scraped content from URL {user_content_url} for tone analysis.")
            else:
                logger.warning(f"Could not fetch content from URL: {user_content_url}. Skipping tone analysis from URL.")
        
        if user_input_content_for_ai:
            return f"""
            **USER'S WRITING STYLE REFERENCE:**
            Below is content provided by the user. Carefully analyze its tone, style, vocabulary, sentence structure, and overall communication approach. When generating your response, mimic this writing style to make the output sound more personal, human, and aligned with the user's voice. Pay attention to formality, enthusiasm, directness, and any specific quirks.
            ---
            {user_input_content_for_ai}
            ---
            """
        else:
            logger.info("No user content provided for tone analysis. Using default AI tone.")
            return ""


    # --- STACK 1: IDEA STACK LOGIC ---
    async def run_idea_stack(self, interest: str, 
                             user_content_text: Optional[str] = None, 
                             user_content_url: Optional[str] = None) -> Dict:
        """
        Orchestrates the full data pipeline for the Idea Stack. It calls upon
        multiple specialist engines in parallel to gather a wide range of data.
        """
        logger.info(f"Running Idea Stack for interest: '{interest}'")
        
        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)

        # Step 1: Define and run all data gathering tasks in parallel.
        # Use a dictionary to keep track of task names for easier error reporting
        tasks = {
            "google_trends": self.google_engine.get_full_keyword_strategy_data(interest), # This already aggregates some, but re-evaluating structure
            "community_insights": self.q_and_a_scraper.run_scraping_tasks(interest),
            "keyword_tool_trends": self.trend_tool_scraper.run_scraper_tasks(interest),
        }

        # Execute tasks concurrently. `return_exceptions=True` ensures that even if one task fails, others complete.
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Unpack results and handle potential exceptions
        google_data = {}
        community_data = []
        keyword_tool_data = []

        if not isinstance(results[0], Exception):
            google_data = results[0]
        else:
            logger.error(f"Google Trends task failed: {results[0]}")
            google_data = {"error": str(results[0])}

        if not isinstance(results[1], Exception):
            community_data = results[1]
        else:
            logger.error(f"Community Insights task failed: {results[1]}")
            community_data = [{"error": str(results[1])}] # Ensure it's still an iterable for JSON dump

        if not isinstance(results[2], Exception):
            keyword_tool_data = results[2]
        else:
            logger.error(f"Keyword Tool Trends task failed: {results[2]}")
            keyword_tool_data = [{"error": str(results[2])}] # Ensure it's still an iterable for JSON dump


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

        {user_tone_instruction}

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

    # --- STACK 2: CONTENT STACK LOGIC ---
    async def run_content_stack(self, interest: str, 
                                  user_content_text: Optional[str] = None, 
                                  user_content_url: Optional[str] = None) -> Dict:
        logger.info(f"Running Content Stack for interest: '{interest}'")
        
        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)

        # Example: Could gather data from google_engine and trend_scraper for content topics
        content_data_tasks = {
            "google_trends_keywords": self.google_engine.get_full_keyword_strategy_data(interest),
            "community_questions": self.q_and_a_scraper.run_scraping_tasks(interest)
        }
        content_results = await asyncio.gather(*content_data_tasks.values(), return_exceptions=True)

        google_keywords = content_results[0] if not isinstance(content_results[0], Exception) else {"error": str(content_results[0])}
        community_questions = content_results[1] if not isinstance(content_results[1], Exception) else [{"error": str(content_results[1])}]

        prompt = f"""
        You are an expert content strategist and SEO specialist. Based on the interest '{interest}' and the following market intelligence, generate 5 compelling blog post titles and a short, engaging description for each. Focus on solving user problems and addressing trending topics.

        --- MARKET INTELLIGENCE ---
        Google Trends & Keyword Data: {json.dumps(google_keywords, indent=2)}
        Community & Q&A Insights: {json.dumps(community_questions, indent=2)}
        --- END REPORT ---

        {user_tone_instruction}

        Format your output as a JSON array of objects, each with "title" and "description" keys.
        """
        return await self._generate_json_response(prompt)


    # --- STACK 3: COMMERCE STACK LOGIC ---
    async def run_commerce_stack(self, product_name: str, 
                                 user_content_text: Optional[str] = None, 
                                 user_content_url: Optional[str] = None,
                                 user_store_url: Optional[str] = None, # User's store for general content audit
                                 marketplace_link: Optional[str] = None, # For sourcing analysis
                                 product_selling_price: Optional[float] = None,
                                 social_platforms_to_sell: Optional[List[str]] = None,
                                 ads_daily_budget: Optional[float] = 10.0,
                                 number_of_days: Optional[int] = 30,
                                 amount_to_buy: Optional[int] = None) -> Dict:
        logger.info(f"Running Commerce Stack for product: '{product_name}'")

        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)

        # We'll use the EcommerceAuditAnalyzer directly here, which already handles its own scraping
        # We need to pass all relevant parameters
        from backend.ecommerce_audit_analyzer import EcommerceAuditAnalyzer # Import locally to avoid circular dep if needed

        analyzer = EcommerceAuditAnalyzer(gemini_api_key=self.model._api_key) # Reuse existing API key
        
        # Pass all relevant parameters to the analyzer, including the pre-generated tone instruction
        return await analyzer.run_audit_and_strategy(
            product_name=product_name,
            user_content_text=user_content_text, # Passed to analyzer for internal tone check (redundant but safe)
            user_content_url=user_content_url,   # Passed to analyzer for internal tone check (redundant but safe)
            user_store_url=user_store_url,
            marketplace_link=marketplace_link,
            product_selling_price=product_selling_price,
            social_platforms_to_sell=social_platforms_to_sell,
            ads_daily_budget=ads_daily_budget,
            number_of_days=number_of_days,
            amount_to_buy=amount_to_buy
            # email_for_report is removed from run_audit_and_strategy, so no need to pass it here
        )

    # --- STACK 4: STRATEGY STACK LOGIC ---
    async def run_strategy_stack(self, interest: str, 
                                 user_content_text: Optional[str] = None, 
                                 user_content_url: Optional[str] = None) -> Dict:
        logger.info(f"Running Strategy Stack for interest: '{interest}'")
        
        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)

        # Gather data from various sources for a comprehensive strategy
        strategy_data_tasks = {
            "google_keywords": self.google_engine.get_full_keyword_strategy_data(interest),
            "community_pain_points": self.q_and_a_scraper.run_scraping_tasks(interest),
            "keyword_tool_insights": self.trend_tool_scraper.run_scraper_tasks(interest),
            # Potentially: self.general_scraper.scrape_multiple_sites(interest, ["competitor_blog", "industry_news"])
        }
        strategy_results = await asyncio.gather(*strategy_data_tasks.values(), return_exceptions=True)

        google_keywords = strategy_results[0] if not isinstance(strategy_results[0], Exception) else {"error": str(strategy_results[0])}
        community_pain_points = strategy_results[1] if not isinstance(strategy_results[1], Exception) else [{"error": str(strategy_results[1])}]
        keyword_tool_insights = strategy_results[2] if not isinstance(strategy_results[2], Exception) else [{"error": str(strategy_results[2])}]

        
        prompt = f"""
        You are a seasoned SEO, content, and digital marketing strategist. Based on the interest '{interest}' and the following comprehensive market intelligence, outline a high-level, actionable digital strategy.

        --- MARKET INTELLIGENCE ---
        Google Keyword and Trend Data: {json.dumps(google_keywords, indent=2)}
        Community Pain Points & Questions: {json.dumps(community_pain_points, indent=2)}
        Keyword Tool Insights: {json.dumps(keyword_tool_insights, indent=2)}
        --- END REPORT ---

        {user_tone_instruction}

        Your output MUST be a valid JSON object with the following keys:
        {{
            "keyword_focus": "Detailed analysis of primary and long-tail keywords based on trends and search volume potential.",
            "content_pillars": "Strategic themes and categories for content creation to address user needs and capture organic traffic.",
            "promotion_channels": "Recommended digital marketing channels (e.g., SEO, social media, paid ads, email) with brief justification.",
            "competitor_analysis_notes": "(Optional: If competitor data was scraped, provide notes here.)",
            "overall_strategic_summary": "A concise, actionable summary of the recommended strategy."
        }}
        """
        return await self._generate_json_response(prompt)
--- END OF FILE backend/engine.py ---