# --- START OF FILE backend/stacks/new_ventures_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

import google.generativeai as genai

from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.marketplace_finder import MarketplaceScout
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class NewVenturesStack:
    """
    A specialized stack for the Prophecy of Beginnings. It synthesizes deep market
    intelligence with a user's personal brief to generate hyper-personalized and
    data-driven business visions.
    """
    def __init__(self, model: genai.GenerativeModel, **seers: Any):
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
        return {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}

    async def prophesy_initial_visions(self, 
                                       interest: str, 
                                       country_code: Optional[str], 
                                       country_name: Optional[str], 
                                       user_tone_instruction: str,
                                       venture_brief: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Phase 1: Generates 10 hyper-personalized and data-driven business visions.
        """
        logger.info(f"NEW VENTURES (PHASE 1): Divining 10 visions for interest: '{interest}'")
        
        # STEP 1: Perform the full, uncompromising RAG ritual.
        retrieved_histories = await self._gather_all_histories(interest, country_code, country_name)
        
        # STEP 2: Construct the definitive, dual-context mega-prompt.
        prompt = f"""
        You are Saga, the Oracle of New Ventures. A mortal seeks your guidance on the broad niche of '{interest}'. You have gathered live market intelligence AND they have provided a personal brief. Your prophecy must be a perfect synthesis of these two sources of truth.

        --- THE SEEKER'S PERSONAL BRIEF ---
        - Preferred Business Model: {venture_brief.get('business_model') if venture_brief else 'Not specified'}
        - Primary Strength: {venture_brief.get('primary_strength') if venture_brief else 'Not specified'}
        - Initial Investment Level: {venture_brief.get('investment_level') if venture_brief else 'Not specified'}
        --- END BRIEF ---

        --- LIVE MARKET INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        --- END INTELLIGENCE ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Analyze the LIVE MARKET INTELLIGENCE to identify the most potent business opportunities (rising trends, unsolved community problems, etc.). Then, filter, adapt, and prioritize these opportunities to generate 10 unique business visions that are perfectly aligned with the SEEKER'S PERSONAL BRIEF. The final visions must be both data-driven and hyper-personalized.

        For each of the 10 visions, you MUST provide:
        1. "prophecy_id": A unique identifier.
        2. "title": A short, captivating name for the business idea.
        3. "one_line_pitch": A single, powerful sentence describing the core concept.
        4. "business_model": The business model (e.g., "E-commerce (Handmade Goods)", "SaaS", "Content & Affiliate").
        5. "evidence_tag": A brief tag indicating the strongest source of market intelligence that supports this idea (e.g., "Rising Google Trend," "Reddit Pain Point," "Niche Forum Discovery").

        Your output MUST be a valid JSON object containing a single key "visions" which is an array of these 10 objects.
        """
        
        initial_prophecy = await get_prophecy_from_oracle(self.model, prompt)
        
        if 'visions' in initial_prophecy and isinstance(initial_prophecy['visions'], list):
            for vision in initial_prophecy['visions']:
                vision['prophecy_id'] = str(uuid.uuid4())

        return {
            "initial_visions": initial_prophecy.get("visions", []),
            "retrieved_histories_for_blueprint": retrieved_histories,
            "user_tone_instruction": user_tone_instruction,
            "country_name": country_name
        }

    async def prophesy_detailed_blueprint(self, chosen_vision: Dict[str, Any], retrieved_histories: Dict[str, Any], user_tone_instruction: str, country_name: str) -> Dict[str, Any]:
        """
        Phase 2: Generates a full business blueprint for a single, chosen vision.
        """
        vision_title = chosen_vision.get("title", "the chosen venture")
        logger.info(f"NEW VENTURES (PHASE 2): Weaving a detailed blueprint for: '{vision_title}'")

        top_keyword = retrieved_histories.get("keyword_runes", {}).get("google_trends", {}).get("rising", [vision_title])[0]
        marketplace_examples = await self.marketplace_oracle.run_marketplace_divination(product_query=top_keyword, marketplace_domain="amazon.com", max_products=5)

        prompt = f"""
        You are Saga, a master strategist. A mortal has chosen to pursue the vision: **'{vision_title}'**. Provide them with the Scroll of Fate—a complete business blueprint.

        **Your prophecy MUST be an actionable plan, grounded entirely in the provided intelligence.**

        --- THE CHOSEN VISION ---
        {json.dumps(chosen_vision, indent=2)}

        --- ORIGINAL MARKET INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        
        --- NEW: Competitor/Sourcing Examples from Amazon ---
        {json.dumps(marketplace_examples, indent=2, default=str)}
        --- END INTELLIGENCE ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Weave a detailed business blueprint as a valid JSON object. The scroll must contain these verses:
        {{
            "prophecy_title": "{vision_title}",
            "summary": "A powerful summary of the business, its mission, and its unique place in the market.",
            "target_audience": "A detailed description of the ideal customer.",
            "marketing_plan": {{
                "content_pillars": ["Pillar 1...", "Pillar 2..."],
                "promotion_channels": ["Channel 1...", "Channel 2..."],
                "unique_selling_proposition": "What makes this venture unique and powerful?"
            }},
            "sourcing_and_operations": "Initial counsel on how to source the product or build the service.",
            "worst_case_monthly_profit_omen": {{
                "scenario": "A realistic, worst-case financial vision for one month.",
                "estimated_revenue": {{"calculation": "e.g., 10 sales @ $50", "value": 500}},
                "estimated_costs": [
                    {{"item": "Cost of Goods", "calculation": "e.g., 10 units @ $15", "value": 150}},
                    {{"item": "Marketing Spend", "value": 100}},
                    {{"item": "Platform Fees (10%)", "value": 50}}
                ],
                "prophesied_profit": {{"calculation": "Revenue - Costs", "value": 200}},
                "counsel": "Your wisdom on this financial omen."
            }},
            "first_three_steps": ["Step 1...", "Step 2...", "Step 3..."]
        }}
        """
        
        return await get_prophecy_from_oracle(self.model, prompt)
# --- END OF FILE backend/stacks/new_ventures_stack.py ---