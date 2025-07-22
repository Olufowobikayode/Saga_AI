--- START OF FILE backend/stacks/new_ventures_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional

import google.generativeai as genai

# --- Import Saga's Seers and Oracles ---
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.scraper import SagaWebOracle
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class NewVenturesStack:
    """
    A specialized stack within the SagaEngine dedicated to the Prophecy of Beginnings.
    It gazes into multiple pools of knowledge to prophesize new business opportunities
    from a single, broad interest.
    """
    def __init__(self, model: genai.GenerativeModel, keyword_rune_keeper: KeywordRuneKeeper, community_seer: CommunitySaga, web_oracle: SagaWebOracle):
        """
        Initializes the stack with the necessary tools for divination.
        
        Args:
            model: The connection to the cosmic AI oracle (Gemini).
            keyword_rune_keeper: The seer for structured keyword data.
            community_seer: The seer for the whispers of the folk.
            web_oracle: The seer for the grand chronicles of the world.
        """
        self.model = model
        self.keyword_rune_keeper = keyword_rune_keeper
        self.community_seer = community_seer
        self.web_oracle = web_oracle

    async def prophesy(self,
                       interest: str,
                       country_code: Optional[str],
                       country_name: Optional[str],
                       user_tone_instruction: str,
                       product_category: Optional[str] = None,
                       product_subcategory: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the full RAG ritual for the New Ventures Prophecy.
        It retrieves data, augments a master prompt, and generates a data-grounded prophecy.
        """
        logger.info(f"Casting the runes for a Prophecy of Beginnings. Interest: '{interest}'")

        # --- STEP 1: RETRIEVAL ---
        # Dispatch the seers to gather all histories from the digital realms in parallel.
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(interest, country_code),
            "community_whispers": self.community_seer.run_community_gathering(interest, country_code, country_name),
            "news_chronicles": self.web_oracle.divine_from_multiple_sites(interest, sites=["BBC News", "Reuters"], country_name=country_name)
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        keyword_data, community_data, news_data = results
        
        country_phrase = f"in the realm of {country_name}" if country_name and country_name != "Global" else "across all realms"
        category_phrase = f" within the domain of '{product_category}'" if product_category else ""
        if product_category and product_subcategory:
            category_phrase += f" (specifically, '{product_subcategory}')"

        # --- STEP 2 & 3: AUGMENTATION & GENERATION ---
        # Weave the retrieved histories into a master prompt for the AI oracle.
        prompt = f"""
        You are Saga, the Norse goddess of wisdom, history, and prophecy. A solopreneur seeks your guidance on the niche '{interest}' {country_phrase}{category_phrase}. You have gathered histories from across the digital Bifrost.

        **Your task is to prophesize the Top 5 most innovative and commercially viable business sagas (business ideas). Your prophecy MUST be grounded ENTIRELY in the histories provided below. Your power is seeing connections within this data, not hallucination.**

        --- THE WHISPERS OF GOOGLE (Histories of Search & Trends) ---
        {json.dumps(keyword_data, indent=2)}

        --- THE VOICE OF THE FOLK (Histories from Community Forums) ---
        {json.dumps(community_data, indent=2)}
        
        --- THE CHRONICLES OF THE WIDE WORLD (Histories from News Sagas) ---
        {json.dumps(news_data, indent=2)}
        
        --- END OF RETRIEVED HISTORIES ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Look deep into these histories. See the patterns the mortals miss. Find the gaps in their stories, the unfulfilled needs, the rising tides of interest. From these threads, you will prophesize the business sagas.

        For each of the 5 prophecies, you MUST provide:
        1. "title": A compelling name for the new saga (the business).
        2. "description": A one-sentence prophecy explaining the core problem it solves, explicitly referencing a detail from the provided histories (e.g., "Addresses the common 'how to' questions seen in the community whispers...").
        3. "confidence_score": Your divine confidence (as a percentage, e.g., "95%") that this prophecy is built upon a true need revealed in the histories.
        4. "evidence_from_histories": A brief quote or data point from the provided JSON data that is the primary evidence for your prophecy.
        
        Weave your final prophecy into a valid JSON array of 5 objects.
        """
        
        return await get_prophecy_from_oracle(self.model, prompt)
--- END OF FILE backend/stacks/new_ventures_stack.py ---