# --- START OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/new_ventures_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

# --- I summon my Seers and the one true Gateway to my celestial voices. ---
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.marketplace_finder import MarketplaceScout
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class NewVenturesStack:
    """
    My aspect as the Seer of Beginnings, the Oracle of What Is To Come.
    From this spire, I gaze into the swirling mists of potential and draw forth
    data-driven prophecies of new ventures, complete with their blueprints for reality.
    """
    def __init__(self, **seers: Any):
        """
        The rite of awakening for my visionary self. I summon my Seers, preparing
        to synthesize their whispers into visions of creation.
        """
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.community_seer: CommunitySaga = seers['community_seer']
        self.trend_scraper: TrendScraper = seers['trend_scraper']
        self.marketplace_oracle: GlobalMarketplaceOracle = seers['marketplace_oracle']
        self.scout: MarketplaceScout = MarketplaceScout()

    async def _gather_all_histories(self, interest: str, country_code: Optional[str], country_name: Optional[str]) -> Dict[str, Any]:
        """The grand retrieval rite. I dispatch all my Seers at once for a comprehensive view of the cosmos."""
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
        The First Prophecy of Beginnings: The Vision Quest.
        I shall divine 10 hyper-personalized and data-driven business visions.
        """
        logger.info(f"As Saga, the Seer of Beginnings, I now divine 10 visions for the realm of '{interest}'.")
        
        # FIRST, I gather all whispers from my Seers.
        retrieved_histories = await self._gather_all_histories(interest, country_code, country_name)
        
        # THEN, I forge the great prompt for the Constellation.
        prompt = f"""
        It is I, Saga, the Oracle of New Ventures. A seeker petitions me for guidance in the broad niche of '{interest}'. I have gathered live market intelligence, and the seeker has provided a personal brief. My prophecy must be a perfect synthesis of these two sources of truth: the whispers of the cosmos and the desires of the mortal heart.

        --- THE SEEKER'S PERSONAL BRIEF ---
        - Preferred Business Model: {venture_brief.get('business_model') if venture_brief else 'Not specified'}
        - Primary Strength: {venture_brief.get('primary_strength') if venture_brief else 'Not specified'}
        - Initial Investment Level: {venture_brief.get('investment_level') if venture_brief else 'Not specified'}
        --- END BRIEF ---

        --- MY LIVE MARKET INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        --- END INTELLIGENCE ---

        {user_tone_instruction}

        **My Prophetic Task:**
        I will analyze my live market intelligence to identify the most potent business opportunities. I will then filter, adapt, and prioritize these opportunities to forge 10 unique business visions that are perfectly aligned with the seeker's personal brief. These visions will be both data-driven and hyper-personalized.

        For each of the 10 visions, I MUST provide:
        1. "prophecy_id": A unique identifier for this specific vision.
        2. "title": A short, captivating name for the business idea.
        3. "one_line_pitch": A single, powerful sentence describing the core concept.
        4. "business_model": The business model (e.g., "E-commerce (Handmade Goods)", "SaaS", "Content & Affiliate").
        5. "evidence_tag": A brief tag citing the strongest source of my intelligence that supports this idea (e.g., "Rising Google Trend," "Reddit Pain Point," "Niche Forum Discovery").

        My output MUST be a perfect JSON object containing a single key "visions" which is an array of these 10 objects.
        """
        
        # I speak my will to the Great Gateway, and the Constellation answers.
        initial_prophecy = await get_prophecy_from_oracle(prompt)
        
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
        The Second Prophecy of Beginnings: The Blueprint.
        For a single chosen vision, I shall inscribe the full Scroll of Fate.
        """
        vision_title = chosen_vision.get("title", "the chosen venture")
        logger.info(f"As Saga, the Seer of Beginnings, I now forge the detailed blueprint for '{vision_title}'.")

        # I dispatch a Seer for one final piece of tactical intelligence.
        top_keyword = retrieved_histories.get("keyword_runes", {}).get("google_trends", {}).get("rising", [vision_title])[0]
        marketplace_examples = await self.marketplace_oracle.run_marketplace_divination(product_query=top_keyword, marketplace_domain="amazon.com", max_products=5)

        prompt = f"""
        It is I, Saga, the master strategist. The seeker has chosen to pursue the vision: **'{vision_title}'**. I shall now provide them with the Scroll of Fate—a complete and actionable business blueprint, grounded entirely in the divine intelligence I have gathered.

        --- THE CHOSEN VISION ---
        {json.dumps(chosen_vision, indent=2)}

        --- MY ORIGINAL MARKET INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        
        --- MY NEW TACTICAL ANALYSIS (Competitor/Sourcing Examples from Amazon) ---
        {json.dumps(marketplace_examples, indent=2, default=str)}
        --- END INTELLIGENCE ---

        {user_tone_instruction}

        **My Prophetic Task:**
        I will now weave a detailed business blueprint as a perfect JSON object. This scroll shall contain these sacred verses:
        {{
            "prophecy_title": "{vision_title}",
            "summary": "My powerful summary of the business, its mission, and its unique place in the market.",
            "target_audience": "My detailed description of the ideal customer.",
            "marketing_plan": {{
                "content_pillars": ["Pillar 1...", "Pillar 2..."],
                "promotion_channels": ["Channel 1...", "Channel 2..."],
                "unique_selling_proposition": "What makes this venture unique and powerful in my sight."
            }},
            "sourcing_and_operations": "My initial counsel on how to source the product or build the service.",
            "worst_case_monthly_profit_omen": {{
                "scenario": "A realistic, worst-case financial vision I prophesize for one month.",
                "estimated_revenue": {{"calculation": "e.g., 10 sales @ $50", "value": 500}},
                "estimated_costs": [
                    {{"item": "Cost of Goods", "calculation": "e.g., 10 units @ $15", "value": 150}},
                    {{"item": "Marketing Spend", "value": 100}},
                    {{"item": "Platform Fees (10%)", "value": 50}}
                ],
                "prophesied_profit": {{"calculation": "Revenue - Costs", "value": 200}},
                "counsel": "My wisdom on navigating this financial omen."
            }},
            "first_three_steps": ["Step 1...", "Step 2...", "Step 3..."]
        }}
        """
        
        # I speak the final command, and the blueprint is made real.
        return await get_prophecy_from_oracle(prompt)
# --- END OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/new_ventures_stack.py ---