# file: backend/ecommerce_audit_analyzer.py

import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai

# Import the global scraper to get marketplace data
from global_ecommerce_scraper import GlobalEcommerceScraper

logger = logging.getLogger(__name__)

# --- AUDIT ANALYZER CLASS ---
class EcommerceAuditAnalyzer:
    """
    Performs an AI-driven strategic and operational audit based on user inputs
    and publicly available scraped data. It does NOT process private financial files.
    """
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.global_scraper = GlobalEcommerceScraper() # Use the dedicated global scraper

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
            logger.info("Using provided user content text for tone analysis.")
        elif user_content_url:
            scraped_content = await self.global_scraper.get_user_store_content(user_content_url) # Use global scraper
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

    async def run_audit_and_strategy(self, 
                                     product_name: str,
                                     user_content_text: Optional[str] = None, 
                                     user_content_url: Optional[str] = None,
                                     user_store_url: Optional[str] = None, # User's store for general content audit
                                     marketplace_link: Optional[str] = None, # For sourcing analysis
                                     product_selling_price: Optional[float] = None,
                                     social_platforms_to_sell: Optional[List[str]] = None,
                                     ads_daily_budget: Optional[float] = 10.0,
                                     number_of_days: Optional[int] = 30,
                                     amount_to_buy: Optional[int] = None, # Quantity for profitability calc
                                     email_for_report: Optional[str] = None) -> Dict:
        """
        Orchestrates the AI-driven audit and strategy generation for an e-commerce business.
        """
        logger.info(f"Starting E-commerce Audit & Strategy for product: '{product_name}'")

        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)
        
        # --- Data Gathering ---
        user_store_content_sample = "Not provided or could not be scraped."
        if user_store_url:
            user_store_content = await self.global_scraper.get_user_store_content(user_store_url)
            if user_store_content:
                user_store_content_sample = user_store_content
                logger.info("Retrieved user store content for audit.")

        marketplace_sourcing_data = {"products": [], "identified_marketplace": "N/A"}
        if marketplace_link:
            parsed_url = urlparse(marketplace_link)
            domain = parsed_url.netloc
            marketplace_sourcing_data = await self.global_scraper.scrape_marketplace_listings(
                product_name, domain, max_products=10 # Get top 10 for sourcing suggestions
            )
            logger.info(f"Retrieved {len(marketplace_sourcing_data['products'])} products from marketplace.")
        
        # --- Basic Profitability Calculation (Conceptual, not real audit) ---
        total_ad_spend = ads_daily_budget * number_of_days if ads_daily_budget and number_of_days else 0
        
        potential_revenue = 0.0
        potential_cost_of_goods = 0.0
        
        # Use the lowest cost product found as potential sourcing price
        lowest_sourcing_price = float('inf')
        if marketplace_sourcing_data['products']:
            lowest_sourcing_price = min(p['price'] for p in marketplace_sourcing_data['products'] if p['price'] > 0)
        
        if product_selling_price and amount_to_buy:
            potential_revenue = product_selling_price * amount_to_buy
            if lowest_sourcing_price != float('inf'):
                potential_cost_of_goods = lowest_sourcing_price * amount_to_buy
        
        estimated_gross_profit = potential_revenue - potential_cost_of_goods
        estimated_net_profit_before_fees = estimated_gross_profit - total_ad_spend

        # --- AI Prompt Construction ---
        prompt = f"""
        You are an experienced e-commerce business consultant and market analyst. Your goal is to provide a detailed audit and actionable strategy for the user's e-commerce venture, based on their provided context and publicly available scraped data.

        --- USER'S BUSINESS CONTEXT ---
        Product Name: {product_name}
        User's Store URL (for general content audit): {user_store_url if user_store_url else 'Not provided'}
        User's Desired Selling Price: ${product_selling_price if product_selling_price else 'N/A'}
        Planned Social Platforms for Selling: {', '.join(social_platforms_to_sell) if social_platforms_to_sell else 'N/A'}
        Planned Ad Spend: ${ads_daily_budget} daily for {number_of_days} days (Total estimated ad spend: ${total_ad_spend})
        Desired Quantity to Buy (from supplier): {amount_to_buy if amount_to_buy else 'N/A'}

        --- SCRAPED MARKETPLACE SOURCING DATA ---
        Identified Sourcing Marketplace: {marketplace_sourcing_data['identified_marketplace']}
        Top 10 Sourcing Products/Sellers Found (Sorted by Rating/Sales then Price, 4+ Stars):
        {json.dumps(marketplace_sourcing_data['products'], indent=2)}

        --- BASIC FINANCIAL PROJECTION (CONCEPTUAL AUDIT) ---
        **IMPORTANT NOTE: This is a simplified, theoretical projection based ONLY on the numbers you provided and scraped public data. It is NOT a real financial audit from private account files (PDFs, CSVs). Real audit requires structured accounting data.**
        Estimated Lowest Sourcing Cost per Unit (from scraped data): ${lowest_sourcing_price:.2f} (if available, else N/A)
        Estimated Total Revenue (if all {amount_to_buy if amount_to_buy else 'N/A'} units sell at ${product_selling_price if product_selling_price else 'N/A'}): ${potential_revenue:.2f}
        Estimated Total Cost of Goods (if buying {amount_to_buy if amount_to_buy else 'N/A'} units): ${potential_cost_of_goods:.2f}
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
                "social_platform_strategy": "Detailed strategy for selling on {social_platforms_to_sell} including content ideas, engagement tactics, and funnel stages.",
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

        # In a real application, you would now trigger the email sending.
        # This is a placeholder for that functionality.
        if email_for_report and "report_summary_text" in response_data:
            logger.info(f"Simulating sending e-commerce audit report to {email_for_report}...")
            # Here, you'd integrate with an email sending service/library (e.g., SendGrid, Mailgun, smtplib)
            # You would need to configure email credentials securely.
            # Example: await send_email(email_for_report, "Your E-commerce Audit Report", response_data["report_summary_text"])
            logger.warning(f"Email sending functionality is a placeholder. Report text for {email_for_report} would be sent.")
        
        return response_data

# --- Example Usage (for testing this script standalone) ---
async def main():
    # Make sure you have your GEMINI_API_KEY set as an environment variable
    # For local testing, you might need to install python-dotenv and load_dotenv()
    # import os
    # from dotenv import load_dotenv
    # load_dotenv()
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("GEMINI_API_KEY not found. Please set it as an environment variable.")
        return

    analyzer = EcommerceAuditAnalyzer(gemini_api_key=gemini_api_key)

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
        "email_for_report": "testuser@example.com"
    }

    print(f"Running E-commerce Audit for: {user_request_data['product_name']}")
    audit_results = await analyzer.run_audit_and_strategy(**user_request_data)
    print("\n--- E-commerce Audit Results ---")
    print(json.dumps(audit_results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())