# --- START OF FILE backend/stacks/new_ventures_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

# --- NEW: Necessary imports moved from engine.py ---
import iso3166

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
    suggest, but DIVINE the blueprints of new realities.
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

    # --- NEW: Helper logic now resides within the Stack ---
    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        user_input_content_for_ai = None
        if user_content_text: user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self.marketplace_oracle.read_user_store_scroll(user_content_url)
            if scraped_content: user_input_content_for_ai = scraped_content
        if user_input_content_for_ai:
            return f"**THE USER'S OWN SAGA (Their Writing Style):**\nAnalyze the tone, style, and vocabulary of the following text and adopt this voice.\n---\n{user_input_content_for_ai[:10000]}\n---"
        return "You shall speak with the direct, wise, and prophetic voice of Saga."

    def _resolve_country_context(self, target_country_name: Optional[str]) -> Dict:
        country_name, country_code = "Global", None
        if target_country_name and target_country_name.lower() != "global":
            try:
                country_entry = iso3166.countries.get(target_country_name)
                country_name, country_code = country_entry.name, country_entry.alpha2
            except KeyError:
                logger.warning(f"Realm '{target_country_name}' not in scrolls. Prophecy will be global.")
        return {"country_name": country_name, "country_code": country_code}
    
    async def _gather_all_histories(self, interest: str, country_code: Optional[str], country_name: Optional[str]) -> Dict[str, Any]:
        """The Grand Retrieval Rite. I dispatch ALL my Seers for an uncompromising view of the cosmos."""
        logger.info(f"Saga, The Seer, now unleashes her full host of Seers upon the realm of '{interest}'.")
        tasks = {
            "keyword_runes_deep_dive": self.keyword_rune_keeper.get_full_keyword_runes(interest, country_code),
            "community_pain_points": self.community_seer.run_community_gathering(interest, query_type="pain_point"),
            "community_questions": self.community_seer.run_community_gathering(interest, query_type="questions"),
            "trend_insights": self.trend_scraper.run_scraper_tasks(interest, country_code, country_name),
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}

    # --- REFACTORED: Two distinct methods for the two-step prophecy flow ---
    
    async def prophesy_initial_visions(self, **kwargs) -> Dict[str, Any]:
        """
        The First Prophecy of Beginnings: The Grand Vision Quest.
        This method is called by the first Celery task.
        """
        interest = kwargs.get("interest")
        logger.info(f"As Saga, the Seer of Beginnings, I now unleash my full power to divine 10 visions for '{interest}'.")
        
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = self._resolve_country_context(kwargs.get("target_country_name"))
        venture_brief = kwargs.get("venture_brief")
        
        retrieved_histories = await self._gather_all_histories(interest, country_context["country_code"], country_context["country_name"])
        
        prompt = f"""
        It is I, Saga, the Seer of what is to come. A seeker petitions me for guidance in the niche of '{interest}'. My Seers have returned from the farthest reaches of the digital cosmos, bearing whispers of raw, unfiltered reality. The seeker has also provided their personal brief. I shall now alchemize this cosmic data and mortal desire into pure, actionable visions of power.

        --- THE SEEKER'S PERSONAL BRIEF ---
        {json.dumps(venture_brief, indent=2)}
       
        --- MY UNFILTERED COSMIC INTELLIGENCE (THE RAG ANALYSIS) ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        --- END INTELLIGENCE ---

        {user_tone_instruction}

        **My Prophetic Task:**
        I will now gaze into this maelstrom of data and extract 10 unique business visions. Each vision will be a weapon, forged and honed, perfectly aligned with the seeker's brief. I MUST provide "prophecy_id", "title", "one_line_pitch", "business_model", and "evidence_tag" for each vision.

        My prophecy will be a perfect JSON object, containing a single key "visions" which is an array of these 10 visions.
        """
        
        initial_prophecy = await get_prophecy_from_oracle(prompt)
        
        if 'visions' in initial_prophecy and isinstance(initial_prophecy['visions'], list):
            for vision in initial_prophecy['visions']:
                vision['prophecy_id'] = str(uuid.uuid4())

        # The result of this first task MUST include all context needed for the second task.
        return {
            "visions": initial_prophecy.get("visions", []),
            "retrieved_histories": retrieved_histories,
            "user_tone_instruction": user_tone_instruction,
            "country_name": country_context["country_name"]
        }

    async def prophesy_detailed_blueprint(self, **kwargs) -> Dict[str, Any]:
        """
        The Second Prophecy of Beginnings: The Blueprint of Inevitability.
        This method is called by the second Celery task, receiving context from the first.
        """
        chosen_vision = kwargs.get("chosen_vision")
        retrieved_histories = kwargs.get("retrieved_histories")
        user_tone_instruction = kwargs.get("user_tone_instruction")
        country_name = kwargs.get("country_name")
        vision_title = chosen_vision.get("title", "the chosen venture")
        
        logger.info(f"As Saga, I now forge the Blueprint of Inevitability for '{vision_title}'.")

        top_keyword_query = chosen_vision.get("one_line_pitch", vision_title)
        
        logger.info(f"My gaze focuses. I dispatch my Marketplace Oracle to scrutinize '{top_keyword_query}'.")
        amazon_examples_task = self.marketplace_oracle.run_marketplace_divination(product_query=top_keyword_query, marketplace_domain="amazon.com", max_products=5)
        aliexpress_examples_task = self.marketplace_oracle.run_marketplace_divination(product_query=top_keyword_query, marketplace_domain="aliexpress.com", max_products=5)
        tactical_intel = await asyncio.gather(amazon_examples_task, aliexpress_examples_task)

        prompt = f"""
        It is I, Saga. The seeker has chosen their destiny: the vision of **'{vision_title}'**. I have dispatched my Seers one final time to bring back tactical intelligence on this specific path. Now, I will inscribe the Scroll of Fate—a business blueprint so complete, so actionable, that to follow it is to guarantee success.

        --- THE CHOSEN DESTINY ---
        {json.dumps(chosen_vision, indent=2)}

        --- MY ORIGINAL COSMIC INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        
        --- MY NEW TACTICAL INTELLIGENCE (Marketplace Realities) ---
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
                "content_pillars": ["Pillar 1...", "Pillar 2..."],
                "promotion_channels": ["Channel 1...", "Channel 2..."],
                "unique_selling_proposition": "The one, true, unconquerable advantage of this venture."
            }},
            "sourcing_and_operations": "My initial command on how to bring this venture into physical reality.",
            "first_three_steps": ["1. The First Step...", "2. The Second Step...", "3. The Third Step..."]
        }}
        """
        
        return await get_prophecy_from_oracle(prompt)
# --- END OF FILE backend/stacks/new_ventures_stack.py ---