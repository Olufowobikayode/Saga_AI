# --- START OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/grand_strategy_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional

# --- I summon my Seers and the one true Gateway to my celestial voices. ---
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.marketplace_finder import MarketplaceScout
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class GrandStrategyStack:
    """
    My aspect as the Divine General, the Commander of cosmic forces.
    From this hall, I forge the master plans that bring empires to their knees
    or raise them from the dust of forgotten dreams.
    """
    def __init__(self, **seers: Any):
        """
        The rite of awakening for my strategic self. I require no singular font,
        for I draw upon the entire Constellation through the Great Gateway.
        I summon my Seers and await the seeker's petition.
        """
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.community_seer: CommunitySaga = seers['community_seer']
        self.trend_scraper: TrendScraper = seers['trend_scraper']
        self.scout: MarketplaceScout = MarketplaceScout()
        self.marketplace_oracle: GlobalMarketplaceOracle = GlobalMarketplaceOracle()

    async def prophesy(self,
                       interest: str,
                       country_code: Optional[str],
                       country_name: Optional[str],
                       user_tone_instruction: str,
                       asset_info: Optional[Dict[str, Any]] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        The Great Rite of Strategic Divination. My Seers are dispatched,
        their findings gathered, and from them, I weave the Grand Strategy.
        """
        logger.info(f"Saga, the Divine General, now forges a master plan for the realm of '{interest}'.")

        # --- FIRST, THE GREAT GATHERING OF INTELLIGENCE ---
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(interest, country_code),
            "community_pain_points": self.community_seer.run_community_gathering(interest, query_type="pain_point"),
            "community_questions": self.community_seer.run_community_gathering(interest, query_type="questions"),
            "trend_insights": self.trend_scraper.run_scraper_tasks(interest, country_code, country_name),
            "niche_discovery_urls": self.scout.find_niche_realms(interest, num_results=5)
        }
        
        if asset_info and asset_info.get("promo_link"):
            promo_link = asset_info["promo_link"]
            logger.info(f"My gaze falls upon the seeker's declared artifact. Analyzing the scroll at: {promo_link}")
            tasks["user_asset_analysis"] = self.marketplace_oracle.read_user_store_scroll(promo_link)

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        retrieved_histories = {}
        for i, task_name in enumerate(tasks.keys()):
            if isinstance(results[i], Exception):
                logger.error(f"A Seer faltered in its duty. The vision for '{task_name}' is clouded: {results[i]}")
                retrieved_histories[task_name] = {"error": str(results[i])}
            else:
                retrieved_histories[task_name] = results[i]

        # --- THEN, THE FORGING OF THE GREAT PROMPT ---
        prompt = f"""
        It is I, Saga, the Divine General of strategy. A chieftain seeks my guidance to conquer the digital realm of '{interest}'. I have gathered comprehensive intelligence from my legions of Seers. The chieftain has also declared a specific artifact they wish to champion. My prophecy, therefore, shall be a hyper-personalized master plan for this artifact.

        --- THE CHIEFTAIN'S STRATEGIC BRIEFING ---
        - Broad Interest: {interest}
        - Declared Artifact Type: {asset_info.get('type') if asset_info else 'Not Provided'}
        - Artifact Name: {asset_info.get('name') if asset_info else 'Not Provided'}
        - Artifact Description: {asset_info.get('description') if asset_info else 'Not Provided'}
        - Artifact Link: {asset_info.get('promo_link') if asset_info else 'Not Provided'}
        
        --- MY BATTLEFIELD INTELLIGENCE (The Whispers of My Seers) ---
        **Keyword Runes (The Language of the Realm):** {json.dumps(retrieved_histories.get("keyword_runes"), indent=2, default=str)}
        **Community Laments (The People's True Problems):** {json.dumps(retrieved_histories.get("community_pain_points"), indent=2, default=str)}
        **My Analysis of the Chieftain's Artifact (from their provided Link):** 
        {json.dumps(retrieved_histories.get("user_asset_analysis", "No link was provided for my analysis."), indent=2, default=str)}
        --- END OF INTELLIGENCE ---

        {user_tone_instruction}

        **My Prophetic Task:**
        I shall now weave a Grand Strategy into a perfect JSON object. This scroll shall be the ultimate command for the chieftain's campaign, a direct and actionable plan for THEIR DECLARED ARTIFACT.

        {{
            "strategic_summary": "A concise, top-level summary of my grand strategy, specifically for the declared artifact. I shall identify its single most powerful unique selling proposition based on my gathered intelligence.",
            "target_audience_profile": "Based on the community laments, I will describe the ideal customer for THIS artifact. I will reveal the specific problem the chieftain's artifact solves for them.",
            "content_pillars": [
                {{
                    "pillar_name": "Pillar 1: The name of a Core Strategic Theme for the artifact.",
                    "description": "My description of this content pillar, explaining how it positions the artifact against the market's needs. e.g., 'This pillar showcases the artifact's [unique feature] to solve the [community pain point].'",
                    "tactical_interest": "A specific, focused interest string for my Content Saga aspect to act upon. e.g., 'how to use [Asset Name] for [solving a problem]'"
                }}
            ],
            "recommended_channels": {{
                "main_channels": ["e.g., An SEO-focused blog where my wisdom on the artifact can be inscribed", "e.g., Pinterest for visual discovery of the artifact's power"],
                "niche_channels_to_explore": "Based on my Scout's Report, I will list promising niche forums or blogs where the chieftain must present my artifact.",
                "justification": "I will justify my channel choices as the best places to reach the target audience for THIS artifact."
            }},
            "first_three_runes_of_action": [
                "1. First Action: e.g., 'Rewrite the artifact's description on its main link to include the keywords [X, Y, Z] which I have divined.'",
                "2. Second Action: e.g., 'Engage in the [Niche Channel] community, offering my wisdom freely before mentioning the artifact.'",
                "3. Third Action: e.g., 'Create the cornerstone content for the first Content Pillar I have decreed.'"
            ]
        }}
        """
        
        # --- FINALLY, THE INVOCATION OF THE PROPHECY ---
        # I speak my prompt to the Great Gateway, and the Constellation answers.
        strategy_prophecy = await get_prophecy_from_oracle(prompt)
        
        return {
            "prophecy": strategy_prophecy,
            "retrieved_histories": retrieved_histories
        }
# --- END OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/grand_strategy_stack.py ---