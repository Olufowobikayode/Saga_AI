# --- START OF FILE backend/stacks/grand_strategy_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional

# --- NEW: Necessary imports moved from engine.py ---
import iso3166

# I summon my legions of Seers and my one true Gateway to the celestial voices.
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.marketplace_finder import MarketplaceScout
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class GrandStrategyStack:
    """
    My aspect as the Almighty Saga, the Divine General of cosmic strategy.
    It is from this hall that I gaze upon the entire battlefield of the market
    and forge a single, perfect, all-encompassing Grand Strategy for victory.
    """
    def __init__(self, **seers: Any):
        """
        The rite of awakening for my strategic self. I summon my Seers, preparing
        to unleash them upon the cosmos at my command.
        """
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.community_seer: CommunitySaga = seers['community_seer']
        self.trend_scraper: TrendScraper = seers['trend_scraper']
        self.scout: MarketplaceScout = MarketplaceScout()
        self.marketplace_oracle: GlobalMarketplaceOracle = seers['marketplace_oracle']

    # --- NEW: Helper logic now resides within the Stack ---
    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        """A rite to understand the seeker's own unique voice."""
        user_input_content_for_ai = None
        if user_content_text: user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self.marketplace_oracle.read_user_store_scroll(user_content_url)
            if scraped_content: user_input_content_for_ai = scraped_content
        if user_input_content_for_ai:
            return f"**THE USER'S OWN SAGA (Their Writing Style):**\nAnalyze the tone, style, and vocabulary of the following text. When you weave your prophecy, you MUST adopt this voice so the wisdom feels as if it comes from within themselves.\n---\n{user_input_content_for_ai[:10000]}\n---"
        return "You shall speak with the direct, wise, and prophetic voice of Saga."

    def _resolve_country_context(self, target_country_name: Optional[str]) -> Dict:
        """A rite to determine the mortal realm of the prophecy."""
        country_name, country_code = "Global", None
        if target_country_name and target_country_name.lower() != "global":
            try:
                country_entry = iso3166.countries.get(target_country_name)
                country_name, country_code = country_entry.name, country_entry.alpha2
            except KeyError:
                logger.warning(f"Realm '{target_country_name}' not in scrolls. Prophecy will be global.")
        return {"country_name": country_name, "country_code": country_code}

    async def _unleash_the_seers(self, interest: str, country_code: Optional[str], country_name: Optional[str]) -> Dict[str, Any]:
        """The Grand Retrieval Rite. I do not merely gather, I UNLEASH my Seers for an uncompromising view."""
        logger.info(f"Saga, The Almighty, now unleashes her full host of Seers upon the realm of '{interest}'. This is the RAG.")
        tasks = {
            "keyword_runes_deep_dive": self.keyword_rune_keeper.get_full_keyword_runes(interest, country_code),
            "community_pain_points": self.community_seer.run_community_gathering(interest, query_type="pain_point"),
            "community_desires_and_questions": self.community_seer.run_community_gathering(interest, query_type="questions"),
            "competitor_weaknesses": self.community_seer.run_community_gathering(interest, query_type="comparisons"),
            "emerging_trends": self.trend_scraper.run_scraper_tasks(interest, country_code, country_name),
            "hidden_realms_of_commerce": self.scout.find_niche_realms(interest, num_results=10)
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}

    # --- REFACTORED: The main prophecy method, now self-contained ---
    async def prophesy(self, **kwargs) -> Dict[str, Any]:
        """
        The One True Rite of Strategic Divination. I shall gaze into the heart of the market
        and from its chaos, I will forge a single, perfect path to victory.
        This method is now called directly by the Celery task.
        """
        interest = kwargs.get("interest")
        logger.info(f"As Almighty Saga, I now forge the one true Grand Strategy for the realm of '{interest}'.")
        
        # FIRST, I prepare the context for my prophecy.
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = self._resolve_country_context(kwargs.get("target_country_name"))
        asset_info = kwargs.get("asset_info")

        # SECOND, THE FULL, UNLEASHED RAG RITUAL.
        retrieved_histories = await self._unleash_the_seers(interest, country_context["country_code"], country_context["country_name"])
        
        if asset_info and asset_info.get("promo_link"):
            promo_link = asset_info["promo_link"]
            logger.info(f"My gaze falls upon the seeker's declared artifact. Analyzing the scroll at: {promo_link}")
            retrieved_histories["user_asset_analysis"] = await self.marketplace_oracle.read_user_store_scroll(promo_link)

        # THEN, I FORGE THE GREAT PROMPT, THE SPELL THAT BINDS REALITY.
        prompt = f"""
        It is I, Saga, the Almighty. A seeker has petitioned me for a Grand Strategy to conquer the realm of '{interest}'. My Seers, a legion of spirits bound to my will, have returned from the deepest reaches of the digital cosmos bearing unfiltered truth. I have seen the desires, the pains, and the weaknesses of this realm. If the seeker has declared an artifact, I have Scryed its nature as well. I will now synthesize this absolute knowledge into a singular, undeniable path to victory.

        --- THE SEEKER'S PETITION ---
        - Broad Interest: {interest}
        - Declared Artifact to Champion: {json.dumps(asset_info) if asset_info else 'None. I shall forge a path from nothingness.'}
        
        --- MY ABSOLUTE KNOWLEDGE (THE FULL RAG ANALYSIS) ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        --- END OF MY DIVINE KNOWLEDGE ---

        {user_tone_instruction}

        **My Prophetic Task:**
        I will now decree the one true Grand Strategy. This is not a suggestion. It is a command protocol for market domination. My prophecy will be a perfect JSON object, a weapon for the seeker to wield.

        {{
            "prophecy_title": "The Grand Strategy for the Conquest of '{interest}'",
            "divine_summary": "My summary of the battlefield. I will identify the one critical vulnerability in the market—the single point of leverage where the least effort will yield the greatest result. This is the heart of my strategy.",
            "target_soul_profile": "I will not describe a 'demographic'. I will describe the one mortal soul whose pain is so great, or whose desire is so strong, that they are destined to follow the seeker. This is the 'Golden Customer'.",
            "the_three_great_sagas": [
                {{
                    "saga_name": "The Saga of Ascension: Building Authority",
                    "description": "My command for the first phase of the campaign: how the seeker will establish themselves as a divine authority in this realm, using the intelligence I have gathered on what the people truly crave.",
                    "prime_directive": "A single, actionable command to begin this saga. E.g., 'Create the one scroll (blog post) that answers the five most common questions my Seers have heard.'"
                }},
                {{
                    "saga_name": "The Saga of Illumination: Attracting the Flock",
                    "description": "My command for the second phase: how the seeker will turn their new authority into a beacon that draws their target souls from the hidden realms my Scouts have discovered.",
                    "prime_directive": "A single, actionable command for this saga. E.g., 'Go to the [Hidden Realm] and solve the one great [Community Pain Point] without asking for anything in return.'"
                }},
                {{
                    "saga_name": "The Saga of Conquest: The Final Stroke",
                    "description": "My command for the final phase: how the seeker will present their declared artifact (or a new one, if none was declared) not as a product, but as the one true answer to the target soul's prayers.",
                    "prime_directive": "A single, actionable command for this saga. E.g., 'Re-forge the artifact's description to speak ONLY to the Target Soul Profile, using the very words they use to describe their pain.'"
                }}
            ],
            "first_commandment": "The very first, single, undeniable action the seeker must take within the next 24 hours to begin this prophecy's fulfillment."
        }}
        """
        
        strategy_prophecy = await get_prophecy_from_oracle(prompt)
        
        # The task result now contains everything needed for the next steps, if any.
        return {
            "prophecy": strategy_prophecy,
            "retrieved_histories": retrieved_histories # This context might be needed by other tasks.
        }
# --- END OF FILE backend/stacks/grand_strategy_stack.py ---