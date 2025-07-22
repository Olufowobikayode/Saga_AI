--- START OF FILE backend/stacks/commerce_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List

import google.generativeai as genai

# --- Import Saga's Seers and Oracles ---
from backend.q_and_a import CommunitySaga
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

# --- A GRIMOIRE OF STRICT RULES ---
SUPPLIER_SELECTION_RULES = """
- The supplier MUST have a rating of 4.0 stars or higher.
- The supplier's store MUST be at least 4 years old, if this data is available.
- The supplier MUST have a history of significant sales, ideally 3,000+ units sold for the product or in general, if this data is available.
- The supplier MUST support a low Minimum Order Quantity (MOQ), ideally 1.
- The product's final landed cost (including product cost, shipping, and fees) MUST be lower than its potential selling price to ensure profit.
"""

class CommerceSagaStack:
    """
    Saga's aspect as the Oracle of Commerce. This powerful stack delivers prophecies
    on audits, arbitrage, social selling, and product routes, all grounded in
    deep market research and strict rules for profitability and quality.
    """
    def __init__(self, model: genai.GenerativeModel, **seers):
        self.model = model
        self.community_seer: CommunitySaga = seers['community_seer']
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.marketplace_oracle: GlobalMarketplaceOracle = seers['marketplace_oracle']

    async def prophesy_commerce_audit(self, audit_type: str, statement_text: Optional[str] = None, store_url: Optional[str] = None) -> Dict[str, Any]:
        """Generates one of the three commerce audit prophecies."""
        logger.info(f"COMMERCE SAGA: Forging a '{audit_type}' prophecy...")

        intel = {}
        if audit_type in ["Store Audit", "Account Prediction"] and store_url:
            intel["user_store_content"] = await self.marketplace_oracle.read_user_store_scroll(store_url)
            product_name_guess = " ".join(store_url.split('/')[-2:]).replace('-', ' ')
            intel["competitor_data"] = await self.marketplace_oracle.divine_marketplace_sagas(product_query=product_name_guess, marketplace_domain="etsy.com")
        
        prompt = f"""
        You are Saga, a master business analyst and financial strategist. A user requires a prophecy of the type: '{audit_type}'. Analyze the provided intelligence and deliver your wisdom.

        --- PROVIDED INTELLIGENCE ---
        **Audit Type:** {audit_type}
        **User's Store URL:** {store_url or 'N/A'}
        **User's Store Content (Scraped):** {intel.get('user_store_content', 'N/A')}
        **Top Competitors (from Etsy):** {json.dumps(intel.get('competitor_data'), indent=2, default=str)}
        **User's Pasted Account Statement Text:**
        ```text
        {statement_text or 'N/A'}
        ```
        --- END INTELLIGENCE ---

        **Your Prophetic Task:**
        Based ONLY on the intelligence provided, generate the requested audit. Your output must be a valid JSON object.

        // --- ACCOUNT AUDIT --- //
        If the audit_type is 'Account Audit', use this JSON structure:
        {{
            "audit_type": "Account Audit",
            "executive_summary": "High-level summary of financial health. State clearly if there is a net profit or loss.",
            "spending_categorization": [
                {{"category": "e.g., Marketing Ads", "total_spent": 1500.50, "percentage_of_total": "35%"}}
            ],
            "financial_counsel": {{
                "invest_more_in": ["Identify categories with high ROI."],
                "reduce_spending_on": ["Identify categories with low ROI."],
                "stop_spending_on": ["Identify clear money sinks."]
            }},
            "investment_suggestions": "Suggest 2-3 general ways to invest profits."
        }}

        // --- STORE AUDIT --- //
        If the audit_type is 'Store Audit', use this JSON structure:
        {{
            "audit_type": "Store Audit",
            "competitive_analysis": "Analyze the user's store vs. competitors. What do they do better?",
            "strategic_recommendations": {{
                "areas_to_invest_in": ["e.g., 'Professional Product Photography'"],
                "ways_to_beat_competitors": ["e.g., 'Offer a unique bundle'"]
            }}
        }}

        // --- ACCOUNT PREDICTION --- //
        If the audit_type is 'Account Prediction', use this JSON structure:
        {{
            "audit_type": "Account Prediction",
            "synthesis": "Combine financial and market data for a holistic view.",
            "unified_action_plan": ["List the 3-5 most critical actions."],
            "future_scenarios": {{
                "prophecy_if_followed": "Best-case scenario for revenue/profit in 1-12 months if plan is followed.",
                "prophecy_if_ignored": "Likely scenario if issues are not addressed."
            }}
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_arbitrage_paths(self, mode: str, product_name: Optional[str] = None, buy_from_url: Optional[str] = None, sell_on_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generates one of the four arbitrage path prophecies."""
        logger.info(f"COMMERCE SAGA: Forging an 'Arbitrage Paths' prophecy (Mode: {mode})...")
        intel = {}
        if not product_name:
            intel["suggested_product_research"] = await self.community_seer.run_community_gathering("products I wish existed", query_type="positive_feedback")

        prompt = f"""
        You are Saga, a master of global trade. A user requires an 'Arbitrage Paths' prophecy for mode: '{mode}'.

        --- USER'S REQUEST ---
        **Mode:** {mode}
        **Product Name:** {product_name or 'Not Provided - You must suggest one.'}
        **Buy From Marketplace:** {buy_from_url or 'N/A'}
        **Sell On Marketplace:** {sell_on_url or 'N/A'}
        **Additional Constraints:** {json.dumps(kwargs)}

        --- SAGA'S RESEARCH ---
        **Products People Need:** {json.dumps(intel.get('suggested_product_research'), indent=2, default=str)}

        --- SAGA'S DECREED RULES ---
        {SUPPLIER_SELECTION_RULES}
        - You MUST estimate and include delivery/shipping fees ($5-$15 average).

        **Your Prophetic Task:**
        Based on the request, your research, and the rules, generate the arbitrage path. You must imagine you have found platforms/sellers that meet all criteria.

        Your output MUST be a valid JSON object:
        {{
            "prophecy_mode": "{mode}",
            "suggested_product": {{"name": "Product name.", "justification": "Why you suggested it."}},
            "arbitrage_path": {{
                "buy_from": {{"platform": "e.g., AliExpress", "seller_name": "Credible Seller", "seller_rating": "4.5+", "seller_age_years": "5+", "units_sold_history": "5000+", "product_cost": "Realistic low cost"}},
                "sell_on": {{"platform": "e.g., Amazon", "estimated_selling_price": "Realistic high price"}}
            }},
            "profit_calculation": {{
                "estimated_revenue_per_item": "Selling price.",
                "estimated_costs_per_item": [{{"item": "Product Cost", "amount": 0}}, {{"item": "Platform Fees (15%)", "amount": 0}}, {{"item": "Shipping", "amount": 0}}],
                "estimated_net_profit_per_item": "Revenue - costs."
            }},
            "counsel": "Your final wisdom."
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_social_selling_saga(self, **kwargs) -> Dict[str, Any]:
        """Generates a complete social selling plan based on user's profit goals."""
        logger.info(f"COMMERCE SAGA: Forging a 'Social Selling Saga' prophecy...")
        
        product_name = kwargs.get('product_name')
        intel = {}
        if product_name:
            intel["top_suppliers"] = await self.marketplace_oracle.divine_marketplace_sagas(product_query=product_name, marketplace_domain="alibaba.com")

        prompt = f"""
        You are Saga, a master social commerce strategist. A user requires a complete plan to sell '{product_name}' on social media, based on specific profit goals.

        --- USER'S GOALS ---
        {json.dumps(kwargs, indent=2)}

        --- SAGA'S RESEARCH ---
        **Top B2B Suppliers Found on Alibaba:** {json.dumps(intel.get('top_suppliers'), indent=2, default=str)}

        --- SAGA'S DECREED RULES ---
        {SUPPLIER_SELECTION_RULES}
        - The final calculated profit MUST meet or exceed the user's 'desired_profit_per_product'.

        **Your Prophetic Task:**
        Find a supplier that meets the rules and construct a full sales plan.

        Your output MUST be a valid JSON object:
        {{
            "chosen_supplier": {{
                "platform": "Alibaba.com",
                "seller_name": "A plausible seller name from your research that meets the rules.",
                "product_cost_per_unit": "The cost that allows the user's profit goal to be met."
            }},
            "financial_plan": {{
                "user_selling_price": {kwargs.get('social_selling_price')},
                "costs_per_unit": [
                    {{"item": "Product Cost", "amount": "Cost from chosen supplier."}},
                    {{"item": "Estimated Platform Fees (10%)", "amount": 0.10 * kwargs.get('social_selling_price', 0)}},
                    {{"item": "Estimated Shipping", "amount": "An estimated shipping fee."}}
                ],
                "final_profit_per_unit": "Selling Price - All Costs.",
                "units_to_sell_to_cover_daily_ads": "Calculation: {kwargs.get('ads_daily_budget')} / (Final Profit Per Unit)."
            }},
            "action_plan": {{
                "units_to_buy": "Suggest a safe starting number of units to buy.",
                "sales_pitch": "A short, powerful pitch to use on the chosen social platform."
            }}
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_product_route(self, location_type: str) -> Dict[str, Any]:
        """Finds a high-profit-margin product to sell either globally or locally."""
        logger.info(f"COMMERCE SAGA: Forging a 'Product Route' prophecy (Location: {location_type})...")
        
        # RAG: Use Saga's full power to find what people need
        intel = {}
        intel["community_needs"] = await self.community_seer.run_community_gathering("what product should I sell online", query_type="questions")
        intel["rising_trends"] = await self.keyword_rune_keeper.get_full_keyword_runes("trending products")

        prompt = f"""
        You are Saga, the Pathfinder of Profit. A user wants you to find a high-margin product to sell, with a focus on a '{location_type}' market.

        --- SAGA'S RESEARCH ---
        **What People Are Asking To Sell:** {json.dumps(intel.get('community_needs'), indent=2, default=str)}
        **General Rising Product Trends:** {json.dumps(intel.get('rising_trends'), indent=2, default=str)}

        --- SAGA'S DECREED RULES ---
        {SUPPLIER_SELECTION_RULES}
        - The product MUST be sourced from a global B2B marketplace (like Alibaba).
        - The potential selling price MUST be significantly higher than the sourcing price.

        **Your Prophetic Task:**
        Based on your research, suggest ONE promising product and its complete route to market.

        Your output MUST be a valid JSON object:
        {{
            "suggested_product": {{
                "name": "A specific product name based on your research.",
                "description": "A brief description of the product and why it's a good opportunity.",
                "justification": "Explain WHY you chose this product, referencing your research."
            }},
            "market_route": {{
                "sourcing": {{
                    "platform": "Alibaba.com",
                    "estimated_cost_per_unit": "A realistic low price for this item in bulk."
                }},
                "selling": {{
                    "platform_suggestion": "The best place to sell this (e.g., 'Local Facebook Marketplace', 'Global via Shopify Store').",
                    "estimated_selling_price": "A realistic high price, ensuring a strong profit margin."
                }}
            }},
            "profit_omen": "A brief summary of the potential profit margin (e.g., 'This path shows a potential 300-500% markup, creating a strong profit opportunity.')."
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

--- END OF FILE backend/stacks/commerce_saga_stack.py ---