# file: backend/social_selling_strategist.py

import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from pytrends.request import TrendReq # For Google Trends integration

# Import the global scraper to get marketplace data
from global_ecommerce_scraper import GlobalEcommerceScraper

logger = logging.getLogger(__name__)

class SocialSellingStrategist:
    """
    Analyzes profitability for selling on social platforms, suggests products,
    and devises marketing strategies based on user inputs and scraped data.
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
        except Exception as e:
            logger.error(f"Failed to generate or parse AI JSON response: {e}")
            return {"error": "AI generation or parsing failed.", "details": str(e)}

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        """Helper to generate AI instruction for mimicking user tone."""
        user_input_content_for_ai = None
        if user_content_text:
            user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self.global_scraper.get_user_store_content(user_content_url)
            if scraped_content:
                user_input_content_for_ai = scraped_content
        
        if user_input_content_for_ai:
            return f"""
            **USER'S WRITING STYLE REFERENCE:**
            ---
            {user_input_content_for_ai}
            ---
            When generating your response, adopt the tone, style, and vocabulary found in the above reference content.
            """
        return ""

    async def _get_trending_keywords(self, interest: str) -> List[str]:
        """Fetches trending related queries from Google Trends."""
        logger.info(f"Fetching Google Trends for trending keywords related to '{interest}'...")
        related_queries_data = await asyncio.to_thread(self.pytrends.related_queries, kw_list=[interest])
        
        trending_list = []
        if interest in related_queries_data and 'rising' in related_queries_data[interest]:
            rising_df = related_queries_data[interest]['rising']
            if not rising_df.empty:
                trending_list = rising_df['query'].tolist()[:5]
        return trending_list

    async def analyze_social_selling(self, 
                                     product_name: str, 
                                     product_selling_price: float,
                                     social_platforms_to_sell: List[str],
                                     ads_daily_budget: float, 
                                     number_of_days: int, 
                                     amount_to_buy: int,
                                     supplier_marketplace_link: Optional[str] = None,
                                     user_content_text: Optional[str] = None,
                                     user_content_url: Optional[str] = None) -> Dict:
        """
        Calculates theoretical profitability for social selling, and suggests strategies.
        """
        logger.info(f"Analyzing social selling for '{product_name}'")

        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)
        
        # --- Data Gathering ---
        # Get supplier pricing
        supplier_data = {"products": [], "identified_marketplace": "N/A"}
        if supplier_marketplace_link:
            parsed_url = urlparse(supplier_marketplace_link)
            domain = parsed_url.netloc
            supplier_data = await self.global_scraper.scrape_marketplace_listings(
                product_name, domain, max_products=5 # Get top 5 suppliers
            )
        else: # If no specific supplier link, try to find a general good sourcing option
             supplier_data = await self.global_scraper.scrape_marketplace_listings(
                product_name, "aliexpress.com", max_products=5 # Default to AliExpress for general sourcing
            )
        
        # Get trending keywords for related product suggestions
        trending_keywords = await self._get_trending_keywords(product_name)

        # --- Profitability Calculation ---
        total_ad_spend = ads_daily_budget * number_of_days
        
        lowest_sourcing_price = float('inf')
        if supplier_data['products']:
            lowest_sourcing_price = min(p['price'] for p in supplier_data['products'] if p['price'] > 0)
        
        if lowest_sourcing_price == float('inf'):
            logger.warning("Could not identify a clear sourcing price. Profitability projection will be limited.")
            cost_per_unit = 0.0
        else:
            cost_per_unit = lowest_sourcing_price

        total_cost_of_goods = cost_per_unit * amount_to_buy
        potential_revenue = product_selling_price * amount_to_buy
        
        estimated_gross_profit = potential_revenue - total_cost_of_goods
        estimated_net_profit_before_fees = estimated_gross_profit - total_ad_spend

        # --- AI Prompt Construction ---
        prompt = f"""
        You are a highly skilled social media marketing and e-commerce expert. Your task is to analyze the profitability of selling '{product_name}' on social platforms and develop a compelling strategy.

        --- USER'S SELLING CONTEXT ---
        Product Name: {product_name}
        Desired Selling Price per Unit: ${product_selling_price:.2f}
        Quantity to Sell (desired purchase): {amount_to_buy} units
        Target Social Platforms: {', '.join(social_platforms_to_sell)}
        Daily Ad Budget: ${ads_daily_budget:.2f}
        Number of Days for Ads: {number_of_days} days
        Total Estimated Ad Spend: ${total_ad_spend:.2f}

        --- SOURCING DATA ---
        Identified Sourcing Marketplace: {supplier_data.get('identified_marketplace', 'N/A')}
        Potential Suppliers/Products (Top 5 from search):
        {json.dumps(supplier_data['products'], indent=2)}
        Lowest Sourcing Cost per Unit Found: ${lowest_sourcing_price:.2f} (Consider this as your Cost of Goods Sold)

        --- TRENDING & RELATED PRODUCT DATA ---
        Trending Keywords/Related Searches for '{product_name}': {', '.join(trending_keywords) if trending_keywords else 'N/A'}

        --- PROFITABILITY PROJECTION (THEORETICAL) ---
        (This is a simplified projection. Actual profit depends on conversion rates, shipping, fees, etc.)
        Potential Total Revenue: ${potential_revenue:.2f} (Selling {amount_to_buy} units at ${product_selling_price:.2f})
        Estimated Total Cost of Goods Sold: ${total_cost_of_goods:.2f}
        Estimated Gross Profit: ${estimated_gross_profit:.2f}
        Estimated Net Profit (before platform fees, shipping, payment processing): ${estimated_net_profit_before_fees:.2f}
        
        --- {user_tone_instruction} ---

        **Your Task: Generate a detailed JSON report with analysis and actionable strategies.**

        Your output MUST be a valid JSON object with the following structure:
        {{
            "profitability_analysis": {{
                "summary": "Assess the profitability potential based on the provided numbers and scraped sourcing costs. Highlight risks and opportunities.",
                "breakeven_point": "Approximate sales volume needed to cover total costs (ad spend + cost of goods).",
                "margin_advice": "Advice on improving profit margins (e.g., pricing, sourcing, reducing other costs)."
            }},
            "social_media_strategy": {{
                "platform_breakdown": [
                    {{"platform": "Facebook Marketplace", "tactics": "Specific ad creative ideas, target audience, content types."}},
                    {{"platform": "Instagram", "tactics": "Influencer marketing, visual content strategy, Reels/Stories."}},
                    // ... for all provided platforms
                ],
                "content_pillars": ["Key themes or topics for social content related to the product."],
                "engagement_tactics": "How to build community and engage potential customers."
            }},
            "ads_campaign_optimization": {{
                "targeting_advice": "Specific audience targeting recommendations for social ads.",
                "creative_suggestions": "Ideas for ad visuals and copy to maximize CTR and conversions.",
                "budget_allocation": "How to allocate the daily ${ads_daily_budget} effectively.",
                "key_metrics_to_track": ["Suggested KPIs to monitor ad performance."]
            }},
            "product_sourcing_suggestions": {{
                "recommended_product_or_niche": "(If no product_name provided, suggest based on trends. If product_name provided, re-affirm or suggest variations based on trends/scraped data).",
                "recommended_suppliers": [
                    {{"supplier_name": "Supplier A", "price": 5.00, "link": "url"}},
                    // ... top 3-5 best suppliers from scraped data
                ],
                "sourcing_tips": "Advice on vetting suppliers, minimum order quantities, and shipping."
            }},
            "scaling_growth_strategies": ["Long-term strategies for growth and expanding beyond initial sales."],
            "overall_summary_for_email": "A concise, actionable summary of the entire analysis, suitable for an email."
        }}
        """
        
        response_data = await self._generate_json_response(prompt)
        return response_data

# --- Example Usage (for testing this script standalone) ---
async def main():
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("GEMINI_API_KEY not found. Please set it as an environment variable.")
        return

    strategist = SocialSellingStrategist(gemini_api_key=gemini_api_key)

    user_request_data = {
        "product_name": "Portable Espresso Maker",
        "product_selling_price": 59.99,
        "social_platforms_to_sell": ["TikTok", "Instagram", "YouTube"],
        "ads_daily_budget": 10.0,
        "number_of_days": 30,
        "amount_to_buy": 200,
        "supplier_marketplace_link": "https://www.aliexpress.com/wholesale?SearchText=portable+espresso+maker",
        "user_content_text": "We're a vibrant brand focused on lifestyle products for young, tech-savvy professionals. Our tone is always energetic and inspiring."
    }

    print(f"Analyzing social selling for: {user_request_data['product_name']}")
    results = await strategist.analyze_social_selling(**user_request_data)
    print("\n--- Social Selling Strategy Results ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main())