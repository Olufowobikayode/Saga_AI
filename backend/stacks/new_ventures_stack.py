--- START OF FILE backend/stacks/new_ventures_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

import google.generativeai as genai

# --- As decreed, this stack imports ALL necessary seers and oracles from the backend ---
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.marketplace_finder import MarketplaceScout
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class NewVenturesStack:
    """
    A specialized stack for the complete, two-phase Prophecy of Beginnings.
    Phase 1 reveals 10 captivating business visions based on a broad interest.
    Phase 2 unveils a detailed business blueprint for a chosen vision.
    This stack has been rebuilt to use Saga's full, enhanced intelligence capabilities.
    """
    def __init__(self, model: genai.GenerativeModel, **seers: Any):
        """Initializes the stack with the connection to the AI oracle and all available seers."""
        self.model = model
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.community_seer: CommunitySaga = seers['community_seer']
        self.trend_scraper: TrendScraper = seers['trend_scraper']
        self.marketplace_oracle: GlobalMarketplaceOracle = seers['marketplace_oracle']
        self.scout: MarketplaceScout = MarketplaceScout()


    async def _gather_all_histories(self, interest: str, country_code: Optional[str], country_name: Optional[str]) -> Dict[str, Any]:
        """The grand retrieval rite, dispatching all seers at once for a comprehensive view."""
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(interest, country_code),
            "community_pain_points": self.community_seer.run_community_gathering(interest, query_type="pain_point"),
            "trend_insights": self.trend_scraper.run_scraper_tasks(interest, country_code, country_name),
            "niche_discovery_urls": self.scout.find_niche_realms(interest, num_results=5)
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # We build a dictionary of the retrieved data to pass between phases.
        retrieved_data = {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}
        return retrieved_data

    async def prophesy_initial_visions(self, interest: str, country_code: Optional[str], country_name: Optional[str], user_tone_instruction: str) -> Dict[str, Any]:
        """
        Phase 1: Generates 10 captivating, high-level business visions.
        """
        logger.info(f"NEW VENTURES (PHASE 1): Divining 10 initial visions for interest: '{interest}'")
        
        # Step 1: Retrieval using the full power of the seers
        retrieved_histories = await self._gather_all_histories(interest, country_code, country_name)
        
        # Step 2 & 3: Augmentation & Generation for the initial visions
        prompt = f"""
        You are Saga, the Norse goddess of wisdom, in your aspect as the Spark of Creation. A mortal seeks your guidance on the broad niche of '{interest}'. You have gathered histories from across the digital realms.

        **Your first task is to reveal 10 captivating and concise business visions. These are but glimpses of possible futures, designed to spark inspiration. They must be intriguing, diverse (e.g., physical product, digital service, content platform), and based on the provided histories.**

        --- COMPREHENSIVE INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        --- END OF INTELLIGENCE ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        From the threads of the retrieved intelligence, prophesize 10 unique business sagas.

        For each of the 10 visions, you MUST provide:
        1. "prophecy_id": A unique identifier for this specific vision.
        2. "title": A short, captivating name for the business idea.
        3. "one_line_pitch": A single, powerful sentence that describes the core concept and the problem it solves.
        4. "business_model": A brief description of the business model (e.g., "E-commerce (Dropshipping)", "SaaS", "Content & Affiliate", "Handmade Goods").
        5. "evidence_tag": A very brief tag indicating the strongest source of inspiration (e.g., "Rising Trend," "Community Pain Point," "Niche Discovery").

        Your output MUST be a valid JSON object containing a single key "visions" which is an array of these 10 objects.
        """
        
        initial_prophecy = await get_prophecy_from_oracle(self.model, prompt)
        
        # Manually add unique IDs for robust tracking
        if 'visions' in initial_prophecy and isinstance(initial_prophecy['visions'], list):
            for vision in initial_prophecy['visions']:
                vision['prophecy_id'] = str(uuid.uuid4())

        # Return both the visions for the user AND the data needed for Phase 2.
        return {
            "initial_visions": initial_prophecy.get("visions", []),
            "retrieved_histories_for_blueprint": retrieved_histories
        }

    async def prophesy_detailed_blueprint(self, chosen_vision: Dict[str, Any], retrieved_histories: Dict[str, Any], user_tone_instruction: str, country_name: str) -> Dict[str, Any]:
        """
        Phase 2: Generates a full business blueprint for a single, chosen vision.
        """
        vision_title = chosen_vision.get("title", "the chosen venture")
        logger.info(f"NEW VENTURES (PHASE 2): Weaving a detailed blueprint for the vision: '{vision_title}'")

        # Use the top keyword from trends to find sourcing/competitor examples
        top_keyword = retrieved_histories.get("keyword_runes", {}).get("google_trends", {}).get("rising", [vision_title])[0]
        marketplace_examples = await self.marketplace_oracle.divine_marketplace_sagas(product_query=top_keyword, marketplace_domain="amazon.com", max_products=5, target_country_code=None)

        prompt = f"""
        You are Saga, the Norse goddess of wisdom, acting as a master strategist. A mortal has chosen to pursue a specific vision you revealed: **'{vision_title}'**. Now, you must provide them with the Scroll of Fate—a complete business blueprint to guide their hand for the {country_name} market.

        **Your prophecy MUST be an actionable plan, grounded entirely in the original histories and new market examples. Do not invent facts.**

        --- THE CHOSEN VISION ---
        {json.dumps(chosen_vision, indent=2)}

        --- ORIGINAL INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        
        --- NEW: Competitor/Sourcing Examples from Amazon for '{top_keyword}' ---
        {json.dumps(marketplace_examples, indent=2, default=str)}
        --- END OF INTELLIGENCE ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Weave a detailed business blueprint as a valid JSON object. The scroll must contain these verses:
        {{
            "prophecy_title": "{vision_title}",
            "summary": "A powerful summary of the business, its mission, and its unique place in the market, based on the data.",
            "target_audience": "A detailed description of the ideal customer. Who are they? What problems from the histories does this solve for them?",
            "marketing_plan": {{
                "content_pillars": ["Pillar 1: e.g., 'Answering 'how-to' questions from Reddit'", "Pillar 2: e.g., 'Showcasing alignment with news trends'"],
                "promotion_channels": ["Channel 1: e.g., 'SEO targeting rising queries'", "Channel 2: e.g., 'Pinterest for visual discovery'"],
                "unique_selling_proposition": "What makes this venture unique and powerful? The one message to rule them all."
            }},
            "sourcing_and_operations": "Initial counsel on how to source the product or build the service. Refer to the Amazon examples. Should they look to AliExpress, find local artisans, or develop software?",
            "worst_case_monthly_profit_omen": {{
                "scenario": "A realistic, worst-case financial vision for one month of operation. Be conservative.",
                "estimated_revenue": {{"calculation": "e.g., 10 sales @ $50/sale", "value": 500}},
                "estimated_costs": [
                    {{"item": "Cost of Goods (for 10 sales)", "calculation": "e.g., 10 units @ $15/unit", "value": 150}},
                    {{"item": "Marketing Spend", "calculation": "e.g., A modest starting ad budget", "value": 100}},
                    {{"item": "Platform Fees (approx. 10%)", "calculation": "e.g., 10% of revenue", "value": 50}}
                ],
                "prophesied_profit": {{"calculation": "Revenue - All Costs", "value": 200}},
                "counsel": "Your wisdom on this financial omen. 'This is a starting point. Focus on increasing sales volume and managing costs to improve this fate.'"
            }},
            "first_three_steps": [
                "Step 1: Your first step on this path is to...",
                "Step 2: Next, you must forge...",
                "Step 3: Then, you will announce your arrival by..."
            ]
        }}
        """
        
        return await get_prophecy_from_oracle(self.model, prompt)
--- END OF FILE backend/stacks/new_ventures_stack.py ---