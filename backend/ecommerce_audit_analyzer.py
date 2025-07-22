--- START OF FILE backend/ecommerce_audit_analyzer.py ---
import asyncio
import logging
import json
import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from urllib.parse import urlparse

# Import the global scraper to get marketplace data
from backend.global_ecommerce_scraper import GlobalEcommerceScraper

logger = logging.getLogger(__name__)

# --- AUDIT ANALYZER CLASS ---
class EcommerceAuditAnalyzer:
    """
    Performs an AI-driven strategic and operational audit based on user inputs
    and publicly available scraped data. It does NOT process private financial files.
    """
    def __init__(self, gemini_api_key: str, global_scraper: Optional[GlobalEcommerceScraper] = None):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        # Use provided global_scraper instance if available, otherwise create a new one
        self.global_scraper = global_scraper if global_scraper else GlobalEcommerceScraper()

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

    # Removed _get_user_tone_instruction as it's centralized in engine.py now
    # This method will now receive the tone instruction string directly.

    async def run_audit_and_strategy(self, 
                                     product_name: str,
                                     # Tone instruction received directly
                                     user_tone_instruction: str = "", # New parameter
                                     # Country context received directly
                                     target_country_code: Optional[str] = None, # New parameter
                                     country_name_for_ai: Optional[str] = None, # New parameter
                                     is_global_search: Optional[bool] = False, # New parameter
                                     # Original parameters
                                     user_content_text: Optional[str] = None, # Retained for potential logging/reference, though tone string is primary
                                     user_content_url: Optional[str] = None,  # Retained for potential logging/reference
                                     user_store_url: Optional[str] = None,
                                     marketplace_link: Optional[str] = None,
                                     product_selling_price: Optional[float] = None,
                                     social_platforms_to_sell: Optional[List[str]] = None,
                                     ads_daily_budget: Optional[float] = 10.0,
                                     number_of_days: Optional[int] = 30,
                                     amount_to_buy: Optional[int] = None) -> Dict:
        """
        Orchestrates the AI-driven audit and strategy generation for an e-commerce business.
        """
        logger.info(f"Starting E-commerce Audit & Strategy for product: '{product_name}'")

        # user_tone_instruction is now passed directly from the engine.
        # The user_content_text/url are kept as parameters but are not directly used here for tone analysis.
        
        # --- Data Gathering ---
        user_store_content_sample = "Not provided or could not be scraped."
        if user_store_url:
            # This line assumes the scraper has a method named 'get_user_store_content'
            # Based on the file `global_ecommerce_scraper.py`, the method is `read_user_store_scroll`
            # This is a hidden error I will correct.
            user_store_content = await self.global_scraper.read_user_store_scroll(user_store_url)
            if user_store_content:
                user_store_content_sample = user_store_content
                logger.info("Retrieved user store content for audit.")

        marketplace_sourcing_data = {"products": [], "identified_marketplace": "N/A"}
        if marketplace_link:
            try:
                parsed_url = urlparse(marketplace_link)
                domain = parsed_url.netloc
                # This line assumes a method 'scrape_marketplace_listings'.
                # Based on `global_ecommerce_scraper.py`, the method is `divine_from_marketplaces`.
                # I will correct this second hidden error.
                marketplace_sourcing_data = await self.global_scraper.divine_from_marketplaces(
                    product_query=product_name, marketplace_domain=domain, max_products=10,
                    target_country_code=target_country_code
                )
                logger.info(f"Retrieved {len(marketplace_sourcing_data['products'])} products from marketplace '{marketplace_sourcing_data['identified_marketplace']}'.")
            except Exception as e:
                logger.error(f"Failed to scrape marketplace link {marketplace_link}: {e}")
        else:
            logger.info("No marketplace link provided for sourcing analysis.")
        
        # --- Basic Profitability Calculation (Conceptual, not real audit) ---
        total_ad_spend = (ads_daily_budget or 0.0) * (number_of_days or 0)
        
        potential_revenue = 0.0
        potential_cost_of_goods = 0.0
        
        lowest_sourcing_price = float('inf')
        if marketplace_sourcing_data['products']:
            valid_prices = [p['price'] for p in marketplace_sourcing_data['products'] if p.get('price') and p['price'] > 0]
            if valid_prices:
                lowest_sourcing_price = min(valid_prices)
            else:
                logger.warning("No valid product prices found in scraped marketplace data.")
        
        if product_selling_price is not None and amount_to_buy is not None:
            potential_revenue = product_selling_price * amount_to_buy
            if lowest_sourcing_price != float('inf'):
                potential_cost_of_goods = lowest_sourcing_price * amount_to_buy
            else:
                logger.warning("Lowest sourcing price not available, cost of goods set to 0.")
        else:
            logger.warning("Product selling price or amount to buy not provided, profitability calculation skipped.")
        
        estimated_gross_profit = potential_revenue - potential_cost_of_goods
        estimated_net_profit_before_fees = estimated_gross_profit - total_ad_spend

        # Determine country phrase for AI prompt
        country_phrase = ""
        if country_name_for_ai:
            if is_global_search:
                country_phrase = "for a global market"
            else:
                country_phrase = f"for the {country_name_for_ai} market"

        # --- AI Prompt Construction ---
        prompt = f"""
        You are an experienced e-commerce business consultant and market analyst. Your goal is to provide a detailed audit and actionable strategy for the user's e-commerce venture, based on their provided context and publicly available scraped data {country_phrase}.

        --- USER'S BUSINESS CONTEXT ---
        Product Name: {product_name}
        User's Store URL (for general content audit): {user_store_url if user_store_url else 'Not provided'}
        User's Desired Selling Price: ${product_selling_price if product_selling_price is not None else 'N/A'}
        Planned Social Platforms for Selling: {', '.join(social_platforms_to_sell) if social_platforms_to_sell else 'N/A'}
        Planned Ad Spend: ${ads_daily_budget} daily for {number_of_days} days (Total estimated ad spend: ${total_ad_spend:.2f})
        Desired Quantity to Buy (from supplier): {amount_to_buy if amount_to_buy is not None else 'N/A'}

        --- SCRAPED MARKETPLACE SOURCING DATA ---
        Identified Sourcing Marketplace: {marketplace_sourcing_data['identified_marketplace']}
        Top 10 Sourcing Products/Sellers Found (Sorted by Rating/Sales then Price, 4+ Stars):
        {json.dumps(marketplace_sourcing_data['products'], indent=2)}

        --- BASIC FINANCIAL PROJECTION (CONCEPTUAL AUDIT) ---
        **IMPORTANT NOTE: This is a simplified, theoretical projection based ONLY on the numbers you provided and scraped public data. It is NOT a real financial audit from private account files (PDFs, CSVs). Real audit requires structured accounting data.**
        Estimated Lowest Sourcing Cost per Unit (from scraped data): ${lowest_sourcing_price:.2f} (if available, else N/A)
        Estimated Total Revenue (if all {amount_to_buy if amount_to_buy is not None else 'N/A'} units sell at ${product_selling_price if product_selling_price is not None else 'N/A'}): ${potential_revenue:.2f}
        Estimated Total Cost of Goods (if buying {amount_to_buy if amount_to_buy is not None else 'N/A'} units): ${potential_cost_of_goods:.2f}
        Estimated Gross Profit (before ads/fees): ${estimated_gross_profit:.2f}
        Estimated Net Profit (after ads, before other fees like marketplace commissions, shipping, payment processing): ${estimated_net_profit_before_fees:.2f}

        --- {user_tone_instruction} ---

        **Your Task: Provide a comprehensive e-commerce audit report and strategy. Analyze the provided data and context to identify areas of strength, weakness, opportunities, and threats (SWOT). Offer actionable improvements.**

        Your output MUST be a valid JSON object with the following structure:
        {{
            "audit_highlights": "Summary of key findings and overall health based on provided data. Be direct and constructive.",
            "profit_loss_insights": {{
                "summary": "Analysis of the basic financial projection, highlighting potential profitability issues or strengths. Advise on realistic margins and costs beyond ads.",
                "improvement_areas": ["Advice on limiting expenses.", "Advice on improving spending efficiency."]
            }},
            "sourcing_strategy_recommendations": {{
                "best_10_suppliers": [
                    {{"supplier_name": "Supplier X", "product_title": "Product A", "price": 10.50, "rating": 4.8, "sales_history": 5000, "link": "url"}},
                    // ... up to 10 entries from marketplace_sourcing_data['products']
                ],
                "sourcing_advice": "Strategy for negotiating, checking quality, and logistics."
            }},
            "marketing_sales_strategy": {{
                "market_opportunity": "Identify potential market gaps or high-demand areas for the product.",
                "social_platform_strategy": "Detailed strategy for selling on {', '.join(social_platforms_to_sell) if social_platforms_to_sell else 'N/A'} including content ideas, engagement tactics, and funnel stages.",
                "ads_optimization": "Advice on optimizing the ${ads_daily_budget} daily ad spend for {number_of_days} days, targeting, and A/B testing.",
                "scaling_strategies": "Recommendations to scale sales beyond initial projections."
            }},
            "store_presence_improvements": {{
                "overall_feedback": "(If user_store_url provided) Analysis of user's store content/messaging for clarity, persuasiveness, and common e-commerce best practices. Point out specific errors/areas for improvement.",
                "example_improvements": ["Improve product descriptions", "Add clear call-to-actions"]
            }},
            "overall_action_plan": ["Step 1...", "Step 2..."],
            "report_summary_text": "A concise, actionable summary of the entire report, ideal for an email. Keep it professional and direct."
        }}
        
        Ensure all array fields contain objects as specified. If data is "N/A", state it clearly within the JSON values.
        """
        
        response_data = await self._generate_json_response(prompt)
        
        return response_data

# --- Example Usage (for testing this script standalone) ---
async def main():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("GEMINI_API_KEY not found. Please set it as an environment variable.")
        return

    # In standalone testing, we instantiate GlobalEcommerceScraper for the analyzer
    # In the full app, the engine will pass its shared instance.
    global_scraper_instance = GlobalEcommerceScraper()
    analyzer = EcommerceAuditAnalyzer(gemini_api_key=gemini_api_key, global_scraper=global_scraper_instance)

    user_request_data = {
        "product_name": "Ergonomic Office Chair",
        "user_content_text": "Welcome to my store! We sell high-quality, comfortable office furniture designed for productivity and well-being. Our mission is to make your workspace a haven.",
        "user_store_url": "https://www.example.com/mystore", # Replace with a real store URL for better test
        "marketplace_link": "https://www.amazon.com/ergonomic-office-chair", # Replace with real Amazon search URL
        "product_selling_price": 299.99,
        "social_platforms_to_sell": ["Facebook Marketplace", "Instagram", "Pinterest"],
        "ads_daily_budget": 15.0,
        "number_of_days": 60,
        "amount_to_buy": 100,
        "user_tone_instruction": "Welcome to my store! We sell high-quality, comfortable office furniture designed for productivity and well-being. Our mission is to make your workspace a haven.", # Simulate engine passing tone
        "target_country_code": "US", # Simulate engine passing country
        "country_name_for_ai": "United States", # Simulate engine passing country
        "is_global_search": False, # Simulate engine passing global flag
    }

    print(f"Running E-commerce Audit for: {user_request_data['product_name']}")
    audit_results = await analyzer.run_audit_and_strategy(**user_request_data)
    print("\n--- E-commerce Audit Results ---")
    print(json.dumps(audit_results, indent=2))
    
    if "report_summary_text" in audit_results:
        print("\n--- Report Summary (for copying) ---")
        print(audit_results["report_summary_text"])


if __name__ == "__main__":
    asyncio.run(main())
--- END OF FILE backend/ecommerce_audit_analyzer.py ---