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
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class GrandStrategyStack:
    """
    The Commander Stack of the SagaEngine. It is the mandatory starting point for any major venture.
    It divines the high-level blueprint for market domination, providing the "Content Pillars"
    that serve as commands for all tactical stacks.
    """
    def __init__(self, model: genai.GenerativeModel, keyword_rune_keeper: KeywordRuneKeeper, community_seer: CommunitySaga, trend_scraper: TrendScraper):
        """
        Initializes the Commander Stack with the necessary seers for strategic divination.
        
        Args:
            model: The connection to the cosmic AI oracle (Gemini).
            keyword_rune_keeper: The seer for structured keyword data.
            community_seer: The seer for the whispers of the folk.
            trend_scraper: The seer for broader keyword trends.
        """
        self.model = model
        self.keyword_rune_keeper = keyword_rune_keeper
        self.community_seer = community_seer
        self.trend_scraper = trend_scraper

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

        # --- STEP 1: COMPREHENSIVE RETRIEVAL ---
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(interest, country_code),
            "community_pain_points": self.community_seer.run_community_gathering(interest, country_code, country_name),
            "trend_insights": self.trend_scraper.run_scraper_tasks(interest, country_code, country_name),
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        keyword_data, community_data, trend_data = results
        
        retrieved_histories = {
            "keyword_runes": keyword_data,
            "community_pain_points": community_data,
            "trend_insights": trend_data
        }

        # --- STEP 2 & 3: AUGMENTATION & GENERATION ---
        prompt = f"""
        You are Saga, the Norse goddess of wisdom, in your aspect as a Divine General. A chieftain has come to you seeking a grand strategy to conquer the digital realm of '{interest}'. You have gathered comprehensive intelligence from your seers.

        **Your task is to forge a master plan for market domination. This prophecy MUST be grounded ENTIRELY in the intelligence provided below. Your strategy must be clear, authoritative, and actionable.**

        --- BATTLEFIELD INTELLIGENCE (Retrieved Histories) ---
        Keyword Runes (The Language of the Realm): {json.dumps(keyword_data, indent=2)}
        Community Laments (The Will of the People): {json.dumps(community_data, indent=2)}
        Seeker Chants (Broader Trends): {json.dumps(trend_data, indent=2)}
        --- END OF INTELLIGENCE ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Weave a Grand Strategy into a valid JSON object. This scroll will be the ultimate command for the chieftain's campaign. It must contain these verses:
        {{
            "strategic_summary": "A concise, top-level summary of the grand strategy. The General's ultimate command.",
            "keyword_focus": "A detailed prophecy on the primary and long-tail keywords. Which words hold power? Which are the sharpest weapons to wield in the SEO battle?",
            "content_pillars": [
                {{
                    "pillar_name": "Pillar 1: Name of the Core Strategic Theme.",
                    "description": "A description of this content pillar and why it is critical, based on the intelligence gathered. e.g., 'This pillar directly addresses the primary pain point found in the community laments.'",
                    "tactical_interest": "A specific, focused interest string derived from this pillar, to be used as a command for the Content Saga stack. e.g., 'sustainable kitchen solutions for small apartments'"
                }},
                //... Generate 3 to 4 such pillars
            ],
            "recommended_channels": "Which realms should the chieftain establish their outposts in? (e.g., SEO-focused blog, Pinterest for visual discovery, Reddit for community engagement). Justify your choices with the intelligence."
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