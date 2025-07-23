import asyncio
import logging
import json
import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from urllib.parse import urlparse

# ### FIX: Imported the correct class 'GlobalMarketplaceOracle' instead of the old 'GlobalEcommerceScraper'.
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle

logger = logging.getLogger(__name__)

class PriceArbitrageFinder:
    """
    A specialist seer within the SagaEngine, tasked with finding 'buy low, sell high'
    opportunities. It divines the hidden paths of value by comparing the price of
    artifacts across different global marketplaces.
    This module is considered a legacy component but has been corrected for functionality.
    The more powerful and comprehensive CommerceSagaStack is the recommended alternative.
    """
    def __init__(self, gemini_api_key: str, global_scraper: Optional[GlobalMarketplaceOracle] = None):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        # ### FIX: Updated the type hint and class instantiation to use the correct 'GlobalMarketplaceOracle'.
        self.global_scraper = global_scraper if global_scraper else GlobalMarketplaceOracle()

    async def _generate_json_response(self, prompt: str) -> Dict:
        """Helper to get a structured JSON prophecy from the AI oracle."""
        try:
            response = await self.model.generate_content_async(prompt)
            json_str = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"The oracle's arbitrage prophecy was not valid JSON: {json_str[:500]}... Error: {e}")
            return {"error": "AI response parsing failed: Invalid JSON.", "details": str(e), "raw_response_snippet": json_str[:500]}
        except Exception as e:
            logger.error(f"Failed to generate an arbitrage prophecy from the AI oracle: {e}")
            return {"error": "AI generation failed.", "details": str(e)}
    
    async def divine_arbitrage_paths(self,
                                     product_name: str,
                                     buy_marketplace_link: str,
                                     sell_marketplace_link: str,
                                     user_tone_instruction: str = "",
                                     target_country_code: Optional[str] = None,
                                     country_name_for_ai: Optional[str] = None,
                                     product_category: Optional[str] = None,
                                     product_subcategory: Optional[str] = None) -> Dict:
        """
        Compares the commercial sagas of a product between two marketplaces to prophesize arbitrage paths.
        """
        logger.info(f"Divining arbitrage paths for '{product_name}' between {buy_marketplace_link} and {sell_marketplace_link}")

        buy_domain = urlparse(buy_marketplace_link).netloc
        sell_domain = urlparse(sell_marketplace_link).netloc

        # RETRIEVAL: Gather the histories from the two marketplaces.
        # This method call was already correct, but the class reference was not.
        buy_task = self.global_scraper.divine_marketplace_sagas(
            product_query=product_name, marketplace_domain=buy_domain, max_products=5, target_country_code=target_country_code
        )
        sell_task = self.global_scraper.divine_marketplace_sagas(
            product_query=product_name, marketplace_domain=sell_domain, max_products=5, target_country_code=target_country_code
        )

        buy_data, sell_data = await asyncio.gather(buy_task, sell_task)
        logger.info(f"Read the saga of {len(buy_data['products'])} artifacts from the buying realm '{buy_data['identified_marketplace']}'.")
        logger.info(f"Read the saga of {len(sell_data['products'])} artifacts from the selling realm '{sell_data['identified_marketplace']}'.")

        context_phrase = f" in the {country_name_for_ai} market" if country_name_for_ai and country_name_for_ai.lower() != "global" else "globally"
        if product_category: context_phrase += f" under the '{product_category}' category"
        if product_subcategory: context_phrase += f" (Subcategory: '{product_subcategory}')"

        # AUGMENTATION & GENERATION: Weave the histories into a prompt for the AI oracle.
        prompt = f"""
        You are an expert e-commerce arbitrage specialist, a seer of hidden value inspired by Saga. Your task is to analyze product listings from two different marketplaces to identify profitable "buy low, sell high" opportunities {context_phrase}. Your analysis and prophecy MUST be based entirely on the data provided below. Do not invent or assume prices.

        --- PRODUCT DETAILS ---
        Artifact Name: {product_name}
        {f"Category: {product_category}" if product_category else ""}
        {f"Subcategory: {product_subcategory}" if product_subcategory else ""}
        
        --- SAGA OF THE BUYING REALM (Data from {buy_domain}) ---
        Identified Realm: {buy_data.get('identified_marketplace', 'N/A')}
        Top Artifacts for Acquiring (potential sourcing):
        {json.dumps(buy_data['products'], indent=2)}

        --- SAGA OF THE SELLING REALM (Data from {sell_domain}) ---
        Identified Realm: {sell_data.get('identified_marketplace', 'N/A')}
        Top Artifacts for Purveying (potential sales):
        {json.dumps(sell_data['products'], indent=2)}

        --- {user_tone_instruction} ---

        **Your Prophetic Task:**
        1.  Analyze the pricing data from both sagas. Your wisdom must come from comparing these two sets of facts.
        2.  Identify specific artifacts that offer strong arbitrage potential (buy from the first realm, sell in the second).
        3.  For each opportunity you divine, you must prophesize:
            *   "buy_product_title": The name of the artifact to acquire.
            *   "buy_marketplace": The realm to acquire it from.
            *   "buy_price": The value to acquire it at, taken directly from the data.
            *   "buy_link": The path to the artifact in the buying realm.
            *   "sell_product_title": The name of the comparable artifact to sell.
            *   "sell_marketplace": The realm to sell it in.
            *   "sell_price": The value to sell it at, taken directly from the data.
            *   "sell_link": The path to the artifact in the selling realm.
            *   "potential_profit_margin_percentage": Your calculated profit margin rune. Calculate this precisely: ((sell_price - buy_price) / buy_price) * 100. Show the calculation.
            *   "counsel": Your wise counsel on this path (e.g., consider shipping costs, listing fees, competition).
        4.  Provide general wisdom on arbitrage strategies.
        5.  Warn of common pitfalls on these hidden paths.

        Format your final prophecy as a valid JSON object:
        {{
            "analysis_summary": "Your overall vision of the arbitrage potential between these two realms for this artifact.",
            "opportunities": [
                {{
                    "buy_product_title": "...", "buy_marketplace": "...", "buy_price": 0.0, "buy_link": "...",
                    "sell_product_title": "...", "sell_marketplace": "...", "sell_price": 0.0, "sell_link": "...",
                    "potential_profit_margin_percentage": 0.0,
                    "counsel": "..."
                }}
            ],
            "general_arbitrage_wisdom": "...",
            "warnings_and_pitfalls": "..."
        }}
        If no profitable paths are revealed in the data, state this clearly in the summary and explain why the sagas do not align for profit.
        """
        
        return await self._generate_json_response(prompt)