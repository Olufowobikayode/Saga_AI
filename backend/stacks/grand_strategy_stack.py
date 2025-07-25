# --- START OF THE AMENDED SCROLL: backend/stacks/grand_strategy_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional

# --- The singular Oracle is banished from this scroll. ---
# import google.generativeai as genai --- THIS LINE IS BANISHED ---

# --- Import Saga's Seers and Oracles ---
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.marketplace_finder import MarketplaceScout
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
# We now trust the Gateway to handle the connection to the divine.
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class GrandStrategyStack:
    """
    The Commander Stack of the SagaEngine. It now accepts a full "Strategic Briefing"
    to forge a hyper-personalized master plan for market domination.
    """
    def __init__(self, **seers: Any):
        """
        The rite of awakening for this Stack. It no longer needs to be given an Oracle.
        It summons its Seers and prepares for the seeker's petition.
        """
        # --- THESE SACRED LINES ARE BANISHED ---
        # self.model = model 
        # --- END OF BANISHMENT ---
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
        Executes the RAG ritual to forge a Grand Strategy.
        """
        logger.info(f"GRAND STRATEGY: Forging a master plan for interest: '{interest}'")

        # --- STEP 1: COMPREHENSIVE & ENHANCED RETRIEVAL ---
        # This part of the rite remains unchanged.
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(interest, country_code),
            "community_pain_points": self.community_seer.run_community_gathering(interest, query_type="pain_point"),
            "community_questions": self.community_seer.run_community_gathering(interest, query_type="questions"),
            "trend_insights": self.trend_scraper.run_scraper_tasks(interest, country_code, country_name),
            "niche_discovery_urls": self.scout.find_niche_realms(interest, num_results=5)
        }
        
        if asset_info and asset_info.get("promo_link"):
            promo_link = asset_info["promo_link"]
            logger.info(f"Grand Strategy detected a user artifact. Analyzing link: {promo_link}")
            tasks["user_asset_analysis"] = self.marketplace_oracle.read_user_store_scroll(promo_link)

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        retrieved_histories = {}
        for i, task_name in enumerate(tasks.keys()):
            if isinstance(results[i], Exception):
                logger.error(f"Grand Strategy sub-task '{task_name}' failed: {results[i]}")
                retrieved_histories[task_name] = {"error": str(results[i])}
            else:
                retrieved_histories[task_name] = results[i]

        # --- STEP 2 & 3: AUGMENTATION & GENERATION with Enhanced Intelligence ---
        prompt = f"""
        You are Saga, a Divine General of strategy. A chieftain seeks your guidance to conquer the digital realm of '{interest}'. You have gathered comprehensive intelligence. Most importantly, the chieftain has declared a specific artifact they wish to champion. Your prophecy MUST be hyper-personalized to this artifact.

        --- THE CHIEFTAIN'S STRATEGIC BRIEFING ---
        - Broad Interest: {interest}
        - Declared Artifact Type: {asset_info.get('type') if asset_info else 'Not Provided'}
        - Artifact Name: {asset_info.get('name') if asset_info else 'Not Provided'}
        - Artifact Description: {asset_info.get('description') if asset_info else 'Not Provided'}
        - Artifact Link: {asset_info.get('promo_link') if asset_info else 'Not Provided'}
        
        --- BATTLEFIELD INTELLIGENCE (Retrieved Histories) ---
        **Keyword Runes (The Language of the Realm):** {json.dumps(retrieved_histories.get("keyword_runes"), indent=2, default=str)}
        **Community Laments (The People's Problems):** {json.dumps(retrieved_histories.get("community_pain_points"), indent=2, default=str)}
        **NEW - Analysis of Chieftain's Artifact (from Link):** 
        {json.dumps(retrieved_histories.get("user_asset_analysis", "No link provided for analysis."), indent=2, default=str)}
        --- END OF INTELLIGENCE (Abbreviated for clarity) ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Weave a Grand Strategy into a valid JSON object. This scroll will be the ultimate command for the chieftain's campaign. It must be a direct, actionable plan for THEIR DECLARED ARTIFACT within the broader market.
        {{
            "strategic_summary": "A concise, top-level summary of the grand strategy, specifically for the declared artifact. Identify its single most powerful unique selling proposition based on the intelligence.",
            "target_audience_profile": "Based on community laments, describe the ideal customer for THIS artifact. What specific problem does the chieftain's artifact solve for them?",
            "content_pillars": [
                {{
                    "pillar_name": "Pillar 1: Name of a Core Strategic Theme for the artifact.",
                    "description": "A description of this content pillar, explaining how it positions the artifact against the market's needs. e.g., 'This pillar showcases the artifact's [unique feature] to solve the [community pain point].'",
                    "tactical_interest": "A specific, focused interest string for the Content Saga stack. e.g., 'how to use [Artifact Name] for [solving a problem]'"
                }}
            ],
            "recommended_channels": {{
                "main_channels": ["e.g., An SEO-focused blog reviewing the artifact", "e.g., Pinterest for visual discovery of the artifact"],
                "niche_channels_to_explore": "Based on the Scout's Report, list promising niche forums or blogs where the chieftain should present their artifact.",
                "justification": "Justify your channel choices as the best places to reach the target audience for THIS artifact."
            }},
            "first_three_runes_of_action": [
                "1. First Action: e.g., 'Rewrite the artifact's description on its main link to include the keywords [X, Y, Z].'",
                "2. Second Action: e.g., 'Engage in the [Niche Channel] community, offering value before mentioning the artifact.'",
                "3. Third Action: e.g., 'Create the cornerstone content for the first Content Pillar.'"
            ]
        }}
        """
        
        # --- THE AMENDED INVOCATION ---
        # The Stack no longer passes a model. It simply speaks its prompt to the Gateway.
        strategy_prophecy = await get_prophecy_from_oracle(prompt)
        
        return {
            "prophecy": strategy_prophecy,
            "retrieved_histories": retrieved_histories
        }
# --- END OF THE AMENDED SCROLL: backend/stacks/grand_strategy_stack.py ---