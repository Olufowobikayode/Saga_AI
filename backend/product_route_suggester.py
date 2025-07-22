--- START OF FILE backend/product_route_suggester.py ---
import asyncio
import logging
import json
import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from pytrends.request import TrendReq
from urllib.parse import urlparse
import iso3166

# Import the global scraper to get marketplace data
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle

logger = logging.getLogger(__name__)

class ProductRouteSuggester:
    """
    A specialist aspect of Saga, the Pathfinder of Creation. It gazes into the
    wilderness of a niche interest and divines a clear path, suggesting a trending
    product and prophesizing the optimal route to source and sell it.
    """
    def __init__(self, gemini_api_key: str, global_scraper: Optional[GlobalMarketplaceOracle] = None):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.global_scraper = global_scraper if global_scraper else GlobalMarketplaceOracle()
        self.pytrends = TrendReq(hl='en-US', tz=360)

    async def _generate_json_response(self, prompt: str) -> Dict:
        """Helper to get a structured JSON prophecy from the AI oracle."""
        try:
            response = await self.model.generate_content_async(prompt)
            json_str = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"The oracle's product route prophecy was not valid JSON: {json_str[:500]}... Error: {e}")
            return {"error": "AI response parsing failed.", "details": str(e), "raw_response_snippet": json_str[:500]}
        except Exception as e:
            logger.error(f"Failed to generate a product route prophecy from the AI oracle: {e}")
            return {"error": "AI generation failed.", "details": str(e)}

    async def _get_trending_keywords_and_topics(self, interest: str, country_code: Optional[str] = None) -> Dict:
        """Listens for trending whispers and topics from Google's oracle."""
        logger.info(f"Listening for trending topics related to '{interest}' in realm '{country_code}'...")
        data = {"related_queries": [], "rising_queries": []}
        try:
            geo_param = country_code.upper() if country_code else ''
            
            await asyncio.to_thread(
                self.pytrends.build_payload, kw_list=[interest], timeframe='today 3-m', geo=geo_param
            )
            related_queries = await asyncio.to_thread(self.pytrends.related_queries)
            
            top = related_queries.get(interest, {}).get('top')
            rising = related_queries.get(interest, {}).get('rising')

            if top is not None and not top.empty:
                data["related_queries"] = top['query'].tolist()[:5]
            if rising is not None and not rising.empty:
                data["rising_queries"] = rising['query'].tolist()[:5]
        except Exception as e:
            logger.error(f"Pytrends oracle failed for interest '{interest}' in realm '{country_code}': {e}")
            data["error"] = str(e)
        return data

    async def prophesy_product_route(self,
                                     niche_interest: str,
                                     user_tone_instruction: str = "",
                                     target_country_name: Optional[str] = None,
                                     product_category: Optional[str] = None,
                                     product_subcategory: Optional[str] = None) -> Dict:
        """
        Suggests a trending product and its optimal sourcing/selling route.
        """
        logger.info(f"Divining a product route for the niche: '{niche_interest}'")

        try:
            country = iso3166.countries.get(target_country_name)
            country_code = country.alpha2
        except (KeyError, AttributeError):
            country_code = None

        # --- RETRIEVAL: Gather Histories of Trends and Bestsellers ---
        # 1. Get trending topics/queries from Google Trends
        trend_data = await self._get_trending_keywords_and_topics(niche_interest, country_code)
        
        # 2. Use the top rising trend to search a general marketplace for inspiration
        search_term = trend_data["rising_queries"][0] if trend_data.get("rising_queries") else niche_interest
        
        logger.info(f"Using top trend '{search_term}' to find exemplary artifacts on Amazon...")
        best_selling_products_data = await self.global_scraper.divine_from_marketplaces(
            product_query=search_term,
            marketplace_domain="amazon.com",
            max_products=10,
            target_country_code=country_code
        )
        best_selling_products = best_selling_products_data.get("products", [])

        context_phrase = f"in the {target_country_name} market" if target_country_name and target_country_name.lower() != "global" else "globally"
        if product_category: context_phrase += f", in the '{product_category}' category"
        if product_subcategory: context_phrase += f" (Subcategory: '{product_subcategory}')"

        # --- AUGMENTATION & GENERATION: The Pathfinder's Prophecy Prompt ---
        prompt = f"""
        You are Saga's Pathfinder, an e-commerce strategist who divines the clearest route from a vague interest to a profitable product. Your task is to analyze market intelligence and prophesize a complete product route for a solopreneur interested in '{niche_interest}' {context_phrase}. Your prophecy MUST be grounded in the intelligence provided below.

        --- MARKET INTELLIGENCE GATHERED ---
        **Niche of Interest**: {niche_interest}
        **Trending Whispers & Rising Tides (from Google's Oracle)**:
        {json.dumps(trend_data, indent=2)}

        **Exemplary Bestselling Artifacts (from a general search on Amazon.com related to trends)**:
        {json.dumps(best_selling_products, indent=2)}

        --- {user_tone_instruction} ---

        **Your Prophetic Task: Suggest a single, promising product and chart its complete e-commerce route.**

        Your output MUST be a valid JSON object, a scroll containing the following prophecies:
        {{
            "suggested_product_prophecy": {{
                "name": "A compelling product name, inspired by the trending whispers and bestselling artifacts.",
                "description": "A brief, enticing description highlighting its appeal and fit within the market's current saga.",
                "justification_from_intelligence": "Explain exactly why this product is a wise choice, explicitly referencing the trend data and bestseller examples. (e.g., 'This aligns with the rising query for 'X' and resembles the popular artifact 'Y').",
                "ideal_selling_price_range": "e.g., $25 - $40"
            }},
            "sourcing_route_prophecy": {{
                "recommended_sourcing_realm": "e.g., AliExpress, Alibaba, Printful.",
                "counsel_on_sourcing": "Wisdom on finding reliable suppliers, checking quality, and navigating the logistics of creation and shipping."
            }},
            "selling_route_prophecy": {{
                "recommended_selling_realms": ["e.g., Amazon FBA", "A personal Shopify store + Instagram Ads", "Etsy"],
                "justification_for_realms": "Why are these the ideal realms to sell this specific artifact?",
                "target_audience_vision": "A clear vision of the ideal customer for this artifact.",
                "marketing_saga_angle": "The core story or unique selling proposition to use when presenting this artifact to the world."
            }},
            "first_steps_on_the_path": [
                "Step 1: The first step on this path is to...",
                "Step 2: Next, you must seek...",
                "Step 3: Then, you will establish your outpost at..."
            ],
            "potential_challenges_on_the_path": ["Possible dangers on this route, such as fierce competition, shipping trolls, or quality control dragons."],
            "pathfinder_summary_for_a_raven": "A concise, inspiring summary of the product opportunity and the prophesized path, fit for a raven's message."
        }}
        """
        
        return await self._generate_json_response(prompt)
--- END OF FILE backend/product_route_suggester.py ---