--- START OF FILE backend/social_selling_strategist.py ---
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

class SocialSellingStrategist:
    """
    A specialist aspect of Saga, the Weaver of Influence. It devises sagas
    for selling on social platforms, analyzing profitability, and crafting
    marketing prophecies based on user goals and divined market data.
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
            logger.error(f"The oracle's social selling prophecy was not valid JSON: {json_str[:500]}... Error: {e}")
            return {"error": "AI response parsing failed.", "details": str(e), "raw_response_snippet": json_str[:500]}
        except Exception as e:
            logger.error(f"Failed to generate a social selling prophecy from the AI oracle: {e}")
            return {"error": "AI generation failed.", "details": str(e)}

    async def _get_trending_keywords(self, interest: str, country_code: Optional[str] = None) -> List[str]:
        """Fetches trending related whispers from Google's oracle."""
        logger.info(f"Listening for trending whispers related to '{interest}' in realm '{country_code}'...")
        trending_list = []
        try:
            geo_param = country_code.upper() if country_code else ''
            
            # This runs in a separate thread to avoid blocking the async event loop
            related_queries_data = await asyncio.to_thread(
                self.pytrends.related_queries, kw_list=[interest], geo=geo_param
            )
            
            rising_df = related_queries_data.get(interest, {}).get('rising')
            if rising_df is not None and not rising_df.empty:
                trending_list = rising_df['query'].tolist()[:5]
        except Exception as e:
            logger.error(f"Pytrends oracle failed for interest '{interest}' in realm '{country_code}': {e}")
        return trending_list

    async def devise_social_selling_saga(self,
                                         product_name: str,
                                         product_selling_price: float,
                                         social_platforms_to_sell: List[str],
                                         ads_daily_budget: float,
                                         number_of_days: int,
                                         amount_to_buy: int,
                                         supplier_marketplace_link: Optional[str] = None,
                                         user_tone_instruction: str = "",
                                         target_country_name: Optional[str] = None,
                                         product_category: Optional[str] = None,
                                         product_subcategory: Optional[str] = None) -> Dict:
        """
        Calculates theoretical profitability for social selling and weaves a complete strategic saga.
        """
        logger.info(f"Weaving a social selling saga for '{product_name}'")

        try:
            country = iso3166.countries.get(target_country_name)
            country_code = country.alpha2
        except (KeyError, AttributeError):
            country_code = None

        # --- RETRIEVAL: Gather Histories from Marketplaces and Trend Oracles ---
        supplier_data_task = self.global_scraper.divine_from_marketplaces(
            product_query=product_name,
            marketplace_domain=urlparse(supplier_marketplace_link).netloc if supplier_marketplace_link else "aliexpress.com", # Default to a common sourcing realm
            max_products=5,
            target_country_code=country_code
        )
        trending_keywords_task = self._get_trending_keywords(product_name, country_code)
        
        supplier_data, trending_keywords = await asyncio.gather(supplier_data_task, trending_keywords_task)

        # --- Weaving the Threads of Profitability ---
        total_ad_spend = (ads_daily_budget or 0.0) * (number_of_days or 0)
        
        lowest_sourcing_price = float('inf')
        if supplier_data['products']:
            valid_prices = [p['price'] for p in supplier_data['products'] if p.get('price') and p['price'] > 0]
            if valid_prices:
                lowest_sourcing_price = min(valid_prices)
        
        cost_per_unit = 0.0 if lowest_sourcing_price == float('inf') else lowest_sourcing_price
        
        total_cost_of_goods = cost_per_unit * (amount_to_buy or 0)
        potential_revenue = (product_selling_price or 0.0) * (amount_to_buy or 0)
        
        estimated_gross_profit = potential_revenue - total_cost_of_goods
        estimated_net_profit_before_fees = estimated_gross_profit - total_ad_spend

        context_phrase = f"for the {target_country_name} market" if target_country_name and target_country_name.lower() != "global" else "for a global audience"
        if product_category: context_phrase += f", in the '{product_category}' category"
        if product_subcategory: context_phrase += f" (Subcategory: '{product_subcategory}')"

        # --- AUGMENTATION & GENERATION: The Grand Prophecy Prompt ---
        prompt = f"""
        You are Saga's Weaver of Influence, a master strategist for social commerce. Your task is to analyze the profitability of selling '{product_name}' and devise a compelling social media saga {context_phrase}. Your prophecy MUST be grounded in the data provided.

        --- THE SOLOPRENEUR'S AMBITION ---
        Product Name: {product_name}
        Desired Selling Price: ${product_selling_price:.2f}
        Target Social Realms: {', '.join(social_platforms_to_sell)}
        Planned Ad Tribute: ${ads_daily_budget:.2f}/day for {number_of_days} days (Total: ${total_ad_spend:.2f})
        Desired Inventory: {amount_to_buy} units

        --- DIVINED HISTORIES ---
        **Sourcing Saga (from {supplier_data.get('identified_marketplace', 'Unknown Realm')})**:
        {json.dumps(supplier_data['products'], indent=2)}
        **Trending Whispers (from Google's Oracle)**:
        {', '.join(trending_keywords) if trending_keywords else 'None heard.'}
        
        --- PROPHECY OF PROFIT (A Vision Based on Provided Numbers) ---
        Lowest Sourcing Cost per Unit: ${cost_per_unit:.2f}
        Total Cost of Goods: ${total_cost_of_goods:.2f}
        Potential Total Revenue: ${potential_revenue:.2f}
        Estimated Gross Profit: ${estimated_gross_profit:.2f}
        Estimated Net Profit (before platform fees, shipping, etc.): ${estimated_net_profit_before_fees:.2f}

        --- {user_tone_instruction} ---

        **Your Task: Weave a detailed JSON scroll with your analysis and actionable prophecies.**

        Your output MUST be a valid JSON object with the following structure:
        {{
            "profitability_prophecy": {{
                "summary": "Assess the profitability potential based on the provided numbers. Highlight the omens of risk and opportunity.",
                "breakeven_point": "Based on the data, calculate the approximate number of sales needed to cover total costs (ad spend + cost of goods). Explain the calculation.",
                "counsel_on_margins": "Wise counsel on improving profit margins (e.g., pricing strategy, sourcing negotiations)."
            }},
            "social_media_saga": {{
                "platform_prophecies": [
                    {{"platform": "Name of Platform", "prophecy": "Specific ad creative ideas, target audience definitions, and content types (e.g., 'Reels showing...', 'Carousel posts explaining...')."}}
                    // ... create one entry for each platform in 'Target Social Realms'
                ],
                "content_pillars_of_the_saga": ["Key themes for social content, drawn from the product's purpose and the trending whispers."],
                "engagement_runes": "How to cast runes of engagement to build a community and converse with potential followers."
            }},
            "ad_campaign_prophecy": {{
                "targeting_wisdom": "Specific audience targeting recommendations for social ads, based on the product and potential customer.",
                "creative_counsel": "Ideas for ad visuals and copy designed to maximize clicks and conversions, referencing the trending whispers.",
                "budget_allocation": "How to wisely allocate the daily ${ads_daily_budget} across the chosen platforms or funnel stages.",
                "runes_to_watch": ["Key metrics (KPIs) to monitor to determine if the ad campaign's prophecy is coming true."]
            }},
            "sourcing_wisdom": {{
                "recommended_sourcing_champion": "Based on the sourcing saga, recommend the best supplier and explain why.",
                "sourcing_counsel": "Advice on vetting suppliers, minimum order quantities, and navigating the shipping seas."
            }},
            "prophecy_summary_for_a_raven": "A concise, actionable summary of the entire analysis, fit for a raven's message."
        }}
        """
        
        return await self._generate_json_response(prompt)
--- END OF FILE backend/social_selling_strategist.py ---