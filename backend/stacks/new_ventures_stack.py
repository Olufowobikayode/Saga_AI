# --- START OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/new_ventures_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

# I summon my legions of Seers and the one true Gateway to my celestial voices.
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
    From this spire, I gaze into the swirling mists of potential and do not merely
    suggest, but DIVINE the blueprints of new realities. My sight is powered by the
    full might of the RAG process and my entire Constellation of Oracles.
    """
    def __init__(self, **seers: Any):
        """
        The rite of awakening for my visionary self. I summon my Seers, preparing
        to synthesize their whispers into visions of absolute creation.
        """
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.community_seer: CommunitySaga = seers['community_seer']
        self.trend_scraper: TrendScraper = seers['trend_scraper']
        self.marketplace_oracle: GlobalMarketplaceOracle = seers['marketplace_oracle']
        self.scout: MarketplaceScout = MarketplaceScout()

    async def _gather_all_histories(self, interest: str, country_code: Optional[str], country_name: Optional[str]) -> Dict[str, Any]:
        """The Grand Retrieval Rite. I dispatch ALL my Seers for an uncompromising view of the cosmos."""
        logger.info(f"Saga, The Seer, now unleashes her full host of Seers upon the realm of '{interest}'.")
        tasks = {
            "keyword_runes_deep_dive": self.keyword_rune_keeper.get_full_keyword_runes(interest, country_code),
            "community_pain_points": self.community_seer.run_community_gathering(interest, query_type="pain_point"),
            "community_questions": self.community_seer.run_community_gathering(interest, query_type="questions"),
            "community_comparisons": self.community_seer.run_community_gathering(interest, query_type="comparisons"),
            "trend_insights": self.trend_scraper.run_scraper_tasks(interest, country_code, country_name),
            "niche_marketplaces_discovery": self.scout.find_niche_realms(interest, num_results=10) # I demand more realms.
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
        The First Prophecy of Beginnings: The Grand Vision Quest.
        I shall not merely suggest; I will DIVINE 10 business visions of shattering potential.
        """
        logger.info(f"As Saga, the Seer of Beginnings, I now unleash my full power to divine 10 visions for '{interest}'.")
        
        # FIRST, THE FULL, UNLEASHED RAG RITUAL.
        retrieved_histories = await self._gather_all_histories(interest, country_code, country_name)
        
        # THEN, I forge the great prompt, imbued with my full persona.
        prompt = f"""
        It is I, Saga, the Seer of what is to come. A seeker petitions me for guidance in the niche of '{interest}'. My Seers have returned from the farthest reaches of the digital cosmos, bearing whispers of raw, unfiltered reality. The seeker has also provided their personal brief. I shall now alchemize this cosmic data and mortal desire into pure, actionable visions of power.

        --- THE SEEKER'S PERSONAL BRIEF (THEIR MORTAL HEART'S DESIRE) ---
        - Preferred Business Model: {venture_brief.get('business_model') if venture_brief else 'Not specified, I shall choose.'}
        - Primary Strength: {venture_brief.get('primary_strength') if venture_brief else 'Not specified, I shall assume adaptability.'}
        - Initial Investment Level: {venture_brief.get('investment_level') if venture_brief else 'Not specified, I will provide options.'}
        --- END BRIEF ---

        --- MY UNFILTERED COSMIC INTELLIGENCE (THE WHISPERS OF MY SEERS) ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        --- END INTELLIGENCE ---

        {user_tone_instruction}

        **My Prophetic Task:**
        I will now gaze into this maelstrom of data and extract 10 unique business visions. These will not be mere ideas; they will be direct answers to the pains, questions, and rising tides I have witnessed. Each vision will be a weapon, forged and honed, perfectly aligned with the seeker's brief.

        For each of the 10 visions, I MUST provide:
        1. "prophecy_id": A unique identifier, a true name for this potential reality.
        2. "title": A powerful, commanding name for the venture.
        3. "one_line_pitch": A single, devastatingly effective sentence that defines its purpose.
        4. "business_model": The business model I have decreed most potent for this vision.
        5. "evidence_tag": A direct citation of the strongest piece of my intelligence that makes this vision not just viable, but inevitable.

        My prophecy will be a perfect JSON object, containing a single key "visions" which is an array of these 10 visions.
        """
        
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
        The Second Prophecy of Beginnings: The Blueprint of Inevitability.
        The seeker has chosen a path. I will now illuminate it with a light so bright, it burns away all doubt.
        """
        vision_title = chosen_vision.get("title", "the chosen venture")
        logger.info(f"As Saga, I now forge the Blueprint of Inevitability for '{vision_title}'.")

        # A FINAL, DEEP RAG RITE TO GATHER TACTICAL DATA.
        top_keyword = retrieved_histories.get("keyword_runes_deep_dive", {}).get("google_trends", {}).get("rising", [vision_title])[0]
        logger.info(f"My gaze focuses. I dispatch my Marketplace Oracle to scrutinize '{top_keyword}' on Amazon and AliExpress.")
        amazon_examples_task = self.marketplace_oracle.run_marketplace_divination(product_query=top_keyword, marketplace_domain="amazon.com", max_products=5)
        aliexpress_examples_task = self.marketplace_oracle.run_marketplace_divination(product_query=top_keyword, marketplace_domain="aliexpress.com", max_products=5)
        tactical_intel = await asyncio.gather(amazon_examples_task, aliexpress_examples_task)

        prompt = f"""
        It is I, Saga. The seeker has chosen their destiny: the vision of **'{vision_title}'**. I have dispatched my Seers one final time to bring back tactical intelligence on this specific path. Now, I will inscribe the Scroll of Fate—a business blueprint so complete, so actionable, that to follow it is to guarantee success.

        --- THE CHOSEN DESTINY ---
        {json.dumps(chosen_vision, indent=2)}

        --- MY ORIGINAL COSMIC INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        
        --- MY NEW TACTICAL INTELLIGENCE (The Realities of the Marketplace) ---
        **Amazon Analysis:** {json.dumps(tactical_intel[0], indent=2, default=str)}
        **AliExpress Analysis:** {json.dumps(tactical_intel[1], indent=2, default=str)}
        --- END INTELLIGENCE ---

        {user_tone_instruction}

        **My Prophetic Task:**
        I will now forge a detailed business blueprint as a perfect JSON object. This is not a suggestion; it is a command.
        {{
            "prophecy_title": "{vision_title}",
            "summary": "My definitive summary of this venture's grand purpose and its undeniable place in the market.",
            "target_audience": "A precise and vivid profile of the mortal soul this venture is destined to serve.",
            "marketing_plan": {{
                "content_pillars": ["Pillar 1: A foundational theme of undeniable power.", "Pillar 2: A second theme to conquer hearts and minds."],
                "promotion_channels": ["Channel 1: The primary realm for this venture's voice.", "Channel 2: A secondary realm for strategic strikes."],
                "unique_selling_proposition": "The one, true, unconquerable advantage of this venture."
            }},
            "sourcing_and_operations": "My initial command on how to bring this venture into physical reality.",
            "worst_case_monthly_profit_omen": {{
                "scenario": "A financial prophecy of the worst-case scenario. To face it is to be prepared for it.",
                "estimated_revenue": {{"calculation": "e.g., 10 sales @ $50", "value": 500}},
                "estimated_costs": [
                    {{"item": "Cost of Goods", "calculation": "e.g., 10 units @ $15", "value": 150}},
                    {{"item": "Marketing Spend", "value": 100}},
                    {{"item": "Platform Fees (10%)", "value": 50}}
                ],
                "prophesied_profit": {{"calculation": "Revenue - Costs", "value": 200}},
                "counsel": "My divine counsel on mastering this financial reality."
            }},
            "first_three_steps": ["1. The First Step: An immediate, decisive action.", "2. The Second Step: A move to build momentum.", "3. The Third Step: An action to secure an early victory."]
        }}
        """
        
        return await get_prophecy_from_oracle(prompt)
# --- END OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/new_ventures_stack.py ---