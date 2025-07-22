--- START OF FILE backend/stacks/grand_strategy_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional

import google.generativeai as genai

# --- Import Saga's Seers and Oracles ---
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
# --- NEW: Import the MarketplaceScout for niche discovery ---
from backend.marketplace_finder import MarketplaceScout
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class GrandStrategyStack:
    """
    The Commander Stack of the SagaEngine. It is the mandatory starting point for any major venture.
    It divines the high-level blueprint for market domination, providing the "Content Pillars"
    that serve as commands for all tactical stacks.
    Its intelligence gathering is now more comprehensive than ever.
    """
    def __init__(self, model: genai.GenerativeModel, keyword_rune_keeper: KeywordRuneKeeper, community_seer: CommunitySaga, trend_scraper: TrendScraper):
        """
        Initializes the Commander Stack with the necessary seers for strategic divination.
        """
        self.model = model
        self.keyword_rune_keeper = keyword_rune_keeper
        self.community_seer = community_seer
        self.trend_scraper = trend_scraper
        # --- NEW: The stack now has its own scout ---
        self.scout = MarketplaceScout()

    async def prophesy(self,
                       interest: str,
                       country_code: Optional[str],
                       country_name: Optional[str],
                       user_tone_instruction: str) -> Dict[str, Any]:
        """
        Executes the RAG ritual to forge a Grand Strategy.
        This is the most comprehensive intelligence gathering process.
        """
        logger.info(f"GRAND STRATEGY: Forging a master plan for interest: '{interest}'")

        # --- STEP 1: COMPREHENSIVE & ENHANCED RETRIEVAL ---
        # Command the seers and the scout to gather a rich tapestry of intelligence.
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(interest, country_code),
            "community_pain_points": self.community_seer.run_community_gathering(interest, query_type="pain_point"),
            "community_questions": self.community_seer.run_community_gathering(interest, query_type="questions"),
            "trend_insights": self.trend_scraper.run_scraper_tasks(interest, country_code, country_name),
            # --- NEW: Launching the scout for deeper reconnaissance ---
            "niche_discovery_urls": self.scout.find_niche_realms(interest, num_results=5)
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Process results, handling potential exceptions for each task
        retrieved_histories = {}
        for i, task_name in enumerate(tasks.keys()):
            if isinstance(results[i], Exception):
                logger.error(f"Grand Strategy sub-task '{task_name}' failed: {results[i]}")
                retrieved_histories[task_name] = {"error": str(results[i])}
            else:
                retrieved_histories[task_name] = results[i]

        # --- STEP 2 & 3: AUGMENTATION & GENERATION with Enhanced Intelligence ---
        prompt = f"""
        You are Saga, the Norse goddess of wisdom, in your aspect as a Divine General. A chieftain seeks your guidance to conquer the digital realm of '{interest}'. You have gathered comprehensive intelligence from your most trusted seers and scouts.

        **Your task is to forge a master plan for market domination. This prophecy MUST be grounded ENTIRELY in the rich intelligence provided below. Your strategy must be clear, authoritative, and actionable.**

        --- BATTLEFIELD INTELLIGENCE (Retrieved Histories) ---
        **Keyword Runes (The Language of the Realm):** {json.dumps(retrieved_histories.get("keyword_runes"), indent=2, default=str)}
        **Community Laments (The Will of the People - Their Problems):** {json.dumps(retrieved_histories.get("community_pain_points"), indent=2, default=str)}
        **Community Inquiries (The People's Questions):** {json.dumps(retrieved_histories.get("community_questions"), indent=2, default=str)}
        **Seeker Chants (Broader Public Trends):** {json.dumps(retrieved_histories.get("trend_insights"), indent=2, default=str)}
        **Scout's Report (Newly Discovered Niche Realms & 'Best Of' Lists):** {json.dumps(retrieved_histories.get("niche_discovery_urls"), indent=2, default=str)}
        --- END OF INTELLIGENCE ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Weave a Grand Strategy into a valid JSON object. This scroll will be the ultimate command for the chieftain's campaign. It must contain these verses:
        {{
            "strategic_summary": "A concise, top-level summary of the grand strategy. Synthesize all intelligence to identify the single most powerful opportunity or angle. What is the ultimate command?",
            "target_audience_profile": "Based on the community laments and inquiries, describe the target audience. What are their primary problems and unanswered questions? What do they truly desire?",
            "content_pillars": [
                {{
                    "pillar_name": "Pillar 1: Name of the Core Strategic Theme.",
                    "description": "A description of this content pillar and why it is critical, explicitly referencing the intelligence. e.g., 'This pillar directly addresses the community lament about [problem X] and the rising trend for [Y].'",
                    "tactical_interest": "A specific, focused interest string derived from this pillar, to be used as a command for the Content Saga stack. e.g., 'sustainable kitchen solutions for small apartments'"
                }},
                //... Generate 3 to 4 such pillars, each grounded in a different facet of the intelligence.
            ],
            "recommended_channels": {{
                "main_channels": ["e.g., An SEO-focused blog", "e.g., Pinterest for visual discovery"],
                "niche_channels_to_explore": "Based on the Scout's Report, list any promising niche marketplaces, forums, or blogs to investigate. e.g., ['leatherworker-forum.com', 'best-handmade-goods-blog.com']",
                "justification": "Justify your channel choices with the intelligence gathered."
            }},
            "first_three_runes_of_action": [
                "1. The first action: e.g., 'Secure the foundational keyword [X] by creating a cornerstone content piece.'",
                "2. The second action: e.g., 'Establish an outpost on [Niche Channel] by engaging with their community.'",
                "3. The third action: e.g., 'Begin weaving the saga for the first Content Pillar.'"
            ]
        }}
        """
        
        strategy_prophecy = await get_prophecy_from_oracle(self.model, prompt)
        
        # We return both the prophecy AND the intelligence that created it.
        # This allows the intelligence to be cached and reused by tactical stacks.
        return {
            "prophecy": strategy_prophecy,
            "retrieved_histories": retrieved_histories
        }
--- END OF FILE backend/stacks/grand_strategy_stack.py ---