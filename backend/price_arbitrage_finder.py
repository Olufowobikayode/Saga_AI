# file: backend/price_arbitrage_finder.py

import asyncio
import logging
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from urllib.parse import urlparse

# Import the global scraper to get marketplace data
from global_ecommerce_scraper import GlobalEcommerceScraper

logger = logging.getLogger(__name__)

class PriceArbitrageFinder:
    """
    Identifies 'buy low, sell high' opportunities by comparing product prices
    across different global marketplaces using AI analysis.
    """
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.global_scraper = GlobalEcommerceScraper()

    async def _generate_json_response(self, prompt: str) -> Dict:
        """Helper to get a structured JSON response from the AI model."""
        try:
            response = await self.model.generate_content_async(prompt)
            json_str = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to generate or parse AI JSON response: {e}")
            return {"error": "AI generation or parsing failed.", "details": str(e)}
    
    async def find_arbitrage_opportunities(self, 
                                           product_name: str, 
                                           buy_marketplace_link: str, 
                                           sell_marketplace_link: str,
                                           user_content_text: Optional[str] = None,
                                           user_content_url: Optional[str] = None) -> Dict:
        """
        Compares prices for a product between two marketplaces to find arbitrage.
        """
        logger.info(f"Finding arbitrage for '{product_name}' between {buy_marketplace_link} and {sell_marketplace_link}")

        user_tone_instruction = await self.global_scraper._get_user_tone_instruction(user_content_text, user_content_url)

        # Parse domains to determine which scraper config to use
        buy_domain = urlparse(buy_marketplace_link).netloc
        sell_domain = urlparse(sell_marketplace_link).netloc

        # Scrape buy marketplace
        buy_data = await self.global_scraper.scrape_marketplace_listings(
            product_name, buy_domain, max_products=5 # Get top 5 for buying
        )
        # Scrape sell marketplace
        sell_data = await self.global_scraper.scrape_marketplace_listings(
            product_name, sell_domain, max_products=5 # Get top 5 for selling
        )

        # Prepare for AI analysis
        prompt = f"""
        You are an expert e-commerce arbitrage specialist. You need to analyze product listings from two different marketplaces to identify profitable "buy low, sell high" opportunities.

        --- PRODUCT DETAILS ---
        Product Name: {product_name}
        
        --- BUY MARKETPLACE DATA (from {buy_domain}) ---
        Identified Marketplace: {buy_data.get('identified_marketplace', 'N/A')}
        Top Products/Sellers for Buying (potential sourcing):
        {json.dumps(buy_data['products'], indent=2)}

        --- SELL MARKETPLACE DATA (from {sell_domain}) ---
        Identified Marketplace: {sell_data.get('identified_marketplace', 'N/A')}
        Top Products/Sellers for Selling (potential sales):
        {json.dumps(sell_data['products'], indent=2)}

        --- {user_tone_instruction} ---

        **Your Task:**
        1.  Analyze the pricing data.
        2.  Identify specific product listings that offer strong arbitrage potential (buy low, sell high).
        3.  For each identified opportunity, clearly state:
            *   "buy_product_title": Title of the product to buy.
            *   "buy_marketplace": Where to buy.
            *   "buy_price": The price to buy at.
            *   "buy_link": Link to the buy listing.
            *   "sell_product_title": Title of the product to sell.
            *   "sell_marketplace": Where to sell.
            *   "sell_price": The price to sell at.
            *   "sell_link": Link to the sell listing.
            *   "potential_profit_margin_percentage": Calculated profit margin (e.g., ((Sell Price - Buy Price) / Buy Price) * 100).
            *   "notes": Any specific considerations (e.g., shipping costs, listing fees, competition).
        4.  Provide general advice on arbitrage strategies.
        5.  Suggest any warnings or common pitfalls.

        Format your final output as a valid JSON object:
        {{
            "analysis_summary": "Overall summary of arbitrage potential.",
            "opportunities": [
                {{
                    "buy_product_title": "...",
                    "buy_marketplace": "...",
                    "buy_price": ...,
                    "buy_link": "...",
                    "sell_product_title": "...",
                    "sell_marketplace": "...",
                    "sell_price": ...,
                    "sell_link": "...",
                    "potential_profit_margin_percentage": ...,
                    "notes": "..."
                }}
            ],
            "arbitrage_strategy_advice": "...",
            "warnings_pitfalls": "..."
        }}
        If no clear opportunities are found, state that in the summary and provide reasons.
        """
        
        return await self._generate_json_response(prompt)

# --- Example Usage (for testing this script standalone) ---
async def main():
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("GEMINI_API_KEY not found. Please set it as an environment variable.")
        return

    finder = PriceArbitrageFinder(gemini_api_key=gemini_api_key)

    product = "gaming headset"
    buy_link = "https://www.aliexpress.com/wholesale?SearchText=gaming+headset"
    sell_link = "https://www.ebay.com/sch/i.html?_nkw=gaming+headset"
    
    print(f"Finding arbitrage for '{product}' between AliExpress and eBay...")
    arbitrage_results = await finder.find_arbitrage_opportunities(product, buy_link, sell_link)
    print("\n--- Arbitrage Finder Results ---")
    print(json.dumps(arbitrage_results, indent=2))

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv() # Load .env for GEMINI_API_KEY
    asyncio.run(main())