--- START OF FILE backend/product_route_suggester.py ---
import asyncio
import logging
import json
import os # Added import for os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from pytrends.request import TrendReq # For Google Trends integration
from urllib.parse import urlparse # Not directly used in this file, but often needed with marketplaces

# Import the global scraper to get marketplace data
from global_ecommerce_scraper import GlobalEcommerceScraper

logger = logging.getLogger(__name__)

class ProductRouteSuggester:
    """
    Suggests trending products and optimal sourcing/selling routes (marketplaces)
    based on market trends and best-selling product analysis.
    """
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.global_scraper = GlobalEcommerceScraper()
        self.pytrends = TrendReq(hl='en-US', tz=360) # Initialize pytrends

    async def _generate_json_response(self, prompt: str) -> Dict:
        """Helper to get a structured JSON response from the AI model."""
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

    async def _get_trending_keywords_and_topics(self, interest: str) -> Dict:
        """Fetches related and rising queries/topics from Google Trends."""
        logger.info(f"Fetching Google Trends data for '{interest}'...")
        data = {"related_queries": [], "rising_queries": []}
        try:
            await asyncio.to_thread(self.pytrends.build_payload, kw_list=[interest], timeframe='today 3-m')
            related_queries = await asyncio.to_thread(self.pytrends.related_queries)
            
            top = related_queries.get(interest, {}).get('top')
            rising = related_queries.get(interest, {}).get('rising')

            if top is not None and not top.empty:
                data["related_queries"] = top['query'].tolist()[:5]
            if rising is not None and not rising.empty:
                data["rising_queries"] = rising['query'].tolist()[:5]
        except Exception as e:
            logger.error(f"Pytrends API failed for interest '{interest}': {e}")
            data["error"] = str(e) # Add error to the data dict
        return data

    async def suggest_product_and_route(self, 
                                        niche_interest: str,
                                        user_tone_instruction: str = "") -> Dict: # Changed parameters
        """
        Suggests a trending product and its optimal sourcing/selling route.
        The user_tone_instruction is passed in from the calling engine.
        """
        logger.info(f"Suggesting product and route for niche: '{niche_interest}'")

        # user_tone_instruction is now expected to be provided by the calling context (e.g., NicheStackEngine)

        # --- Data Gathering ---
        # 1. Get trending topics/queries from Google Trends
        trend_data = await self._get_trending_keywords_and_topics(niche_interest)
        
        # 2. Scrape best-selling products from a general marketplace (e.g., Amazon.com) related to trending queries
        best_selling_products_from_general_search = []
        # Use primary interest or first trending query as search term
        search_term = niche_interest # Default to niche interest
        if trend_data["rising_queries"]:
            search_term = trend_data["rising_queries"][0] # Use the top rising query if available
        
        if search_term:
            try:
                general_marketplace_data = await self.global_scraper.scrape_marketplace_listings(
                    search_term, "amazon.com", max_products=10 # Get top 10 from a major platform
                )
                best_selling_products_from_general_search = general_marketplace_data["products"]
                logger.info(f"Scraped {len(best_selling_products_from_general_search)} products from Amazon.com for search term '{search_term}'.")
            except Exception as e:
                logger.error(f"Failed to scrape Amazon.com for '{search_term}': {e}")
        else:
            logger.warning("No valid search term derived for general marketplace scraping.")


        # --- AI Prompt Construction ---
        prompt = f"""
        You are an innovative e-commerce product researcher and market strategist. Your goal is to identify a promising product within the '{niche_interest}' niche and outline an optimal "route" for a solopreneur to source and sell it for profit.

        --- MARKET INTELLIGENCE ---
        Niche/Interest: {niche_interest}
        Google Trends Data:
        {json.dumps(trend_data, indent=2)}

        Best-Selling Products (from general search on Amazon.com related to trends):
        {json.dumps(best_selling_products_from_general_search, indent=2)}

        --- {user_tone_instruction} ---

        **Your Task: Suggest a product and its complete e-commerce route.**

        Your output MUST be a valid JSON object with the following structure:
        {{
            "suggested_product": {{
                "name": "Compelling product name based on trends and sales data.",
                "description": "Brief, enticing description highlighting its appeal and market fit.",
                "why_this_product": "Explain why this product is a good opportunity, referencing trend data and market demand.",
                "ideal_selling_price_range": "e.g., $20 - $35"
            }},
            "sourcing_route": {{
                "recommended_marketplace": "e.g., AliExpress, Alibaba, etc.",
                "sample_suppliers": [
                    {{"supplier_name": "Supplier A", "product_example": "Exact product name/link", "estimated_cost_per_unit": 5.00, "link": "url"}},
                    // ... up to 3 strong supplier examples from scraped data
                ],
                "sourcing_strategy": "Advice on MOQ, quality control, negotiation, and shipping."
            }},
            "selling_route": {{
                "recommended_platforms": ["e.g., Amazon FBA", "Shopify + Instagram Ads", "Etsy"],
                "justification": "Why these platforms are ideal for this product.",
                "target_audience": "Who to target for this product.",
                "marketing_angle": "Key messaging or unique selling proposition."
            }},
            "initial_strategy_overview": [
                "Step 1: Validate demand further...",
                "Step 2: Order small batch from recommended supplier...",
                "Step 3: Set up chosen selling platform..."
            ],
            "potential_challenges": ["Possible hurdles like competition, shipping delays, quality control."],
            "overall_report_summary": "A concise, inspiring summary of the product opportunity and recommended path."
        }}
        """
        
        response_data = await self._generate_json_response(prompt)
        return response_data

# --- Example Usage (for testing this script standalone) ---
async def main():
    import os
    from dotenv import load_dotenv
    load_dotenv() # Load .env for GEMINI_API_KEY

    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("GEMINI_API_KEY not found. Please set it as an environment variable.")
        return

    suggester = ProductRouteSuggester(gemini_api_key=gemini_api_key)

    niche = "eco-friendly home goods"
    # user_content_sample_url = "https://www.treehugger.com/about-us-4858908" # Example for tone - now handled by engine
    
    print(f"Suggesting product and route for niche: '{niche}'")
    # In standalone testing, we just pass an empty string for tone instruction.
    # In a real API call via the NicheStackEngine, this would be populated.
    results = await suggester.suggest_product_and_route(niche, user_tone_instruction="")
    print("\n--- Product Route Suggestion Results ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
--- END OF FILE backend/product_route_suggester.py ---