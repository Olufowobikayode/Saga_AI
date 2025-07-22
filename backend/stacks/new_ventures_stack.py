--- START OF FILE backend/stacks/new_ventures_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

import google.generativeai as genai

# --- As decreed, this stack imports ALL necessary seers and oracles from the backend ---
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.scraper import SagaWebOracle
from backend.trends import TrendScraper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class NewVenturesStack:
    """
    A specialized stack for the complete, two-phase Prophecy of Beginnings.
    Phase 1 reveals 10 captivating visions.
    Phase 2 unveils a detailed business blueprint for a chosen vision.
    """
    def __init__(self, model: genai.GenerativeModel, **seers: Any):
        """Initializes the stack with the connection to the AI oracle and all available seers."""
        self.model = model
        self.seers = seers

    async def _gather_all_histories(self, interest: str, country_code: Optional[str], country_name: Optional[str]) -> Dict[str, Any]:
        """The grand retrieval rite, dispatching all seers at once."""
        tasks = {
            "keyword_runes": self.seers['keyword_rune_keeper'].get_full_keyword_runes(interest, country_code),
            "community_whispers": self.seers['community_seer'].run_community_gathering(interest, country_code, country_name),
            "news_chronicles": self.seers['web_oracle'].divine_from_multiple_sites(interest, sites=["Reuters", "BBC News"], country_name=country_name),
            "trend_data": self.seers['trend_scraper'].run_scraper_tasks(interest, country_code, country_name),
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # We build a dictionary of the retrieved data to pass between phases.
        retrieved_data = {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}
        return retrieved_data

    async def prophesy_initial_visions(self, interest: str, country_code: Optional[str], country_name: Optional[str], user_tone_instruction: str) -> Dict[str, Any]:
        """
        Phase 1: Generates 10 captivating, high-level business visions.
        """
        logger.info(f"PHASE 1: Divining 10 initial visions for interest: '{interest}'")
        
        # Step 1: Retrieval
        retrieved_histories = await self._gather_all_histories(interest, country_code, country_name)
        
        # Step 2 & 3: Augmentation & Generation for the initial visions
        prompt = f"""
        You are Saga, the Norse goddess of wisdom. A mortal seeks your guidance on the niche '{interest}'. You have gathered histories from across the digital realms.

        **Your first task is to reveal 10 captivating and concise business visions. These are but glimpses of possible futures, designed to spark inspiration. They must be intriguing and based on the provided histories.**

        --- RETRIEVED HISTORIES (Condensed for this Task) ---
        {json.dumps(retrieved_histories, indent=2)}
        --- END OF HISTORIES ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        From the threads of the retrieved histories, prophesize 10 unique business sagas.

        For each of the 10 visions, you MUST provide:
        1. "prophecy_id": A unique identifier for this specific vision. Generate a new one for each.
        2. "title": A short, captivating name for the business idea.
        3. "one_line_pitch": A single, powerful sentence that describes the core concept and hints at the problem it solves.
        4. "evidence_tag": A very brief tag indicating the strongest source of inspiration (e.g., "Rising Trend," "Community Pain Point," "News-Driven").

        Your output MUST be a valid JSON object containing a single key "visions" which is an array of these 10 objects.
        Example: {{"visions": [{{"prophecy_id": "...", "title": "...", ...}}]}}
        """
        
        initial_prophecy = await get_prophecy_from_oracle(self.model, prompt)
        
        # We must return both the visions for the user AND the data for Phase 2.
        return {
            "initial_visions": initial_prophecy,
            "retrieved_histories_for_blueprint": retrieved_histories # Pass this to the next phase
        }

    async def prophesy_detailed_blueprint(self, chosen_vision: Dict[str, Any], retrieved_histories: Dict[str, Any], user_tone_instruction: str) -> Dict[str, Any]:
        """
        Phase 2: Generates a full business blueprint for a single, chosen vision.
        """
        vision_title = chosen_vision.get("title", "the chosen venture")
        logger.info(f"PHASE 2: Weaving a detailed blueprint for the vision: '{vision_title}'")

        # Step 1 is already complete (we use the passed-in histories).
        # Step 2 & 3: A new, deeper Augmentation & Generation for the blueprint.
        prompt = f"""
        You are Saga, the Norse goddess of wisdom, acting as a master strategist. A mortal has chosen to pursue a specific vision you revealed: **'{vision_title}'**. Now, you must provide them with the Scroll of Fate—a complete business blueprint to guide their hand.

        **Your prophecy MUST be an actionable plan, grounded entirely in the original histories you gathered. Do not invent facts.**

        --- THE CHOSEN VISION ---
        {json.dumps(chosen_vision, indent=2)}

        --- ORIGINAL HISTORIES (Use this data to build the blueprint) ---
        {json.dumps(retrieved_histories, indent=2)}
        --- END OF HISTORIES ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Weave a detailed business blueprint as a valid JSON object. The scroll must contain these verses:
        {{
            "prophecy_title": "{vision_title}",
            "summary": "A powerful summary of the business, its mission, and its unique place in the market, based on the data.",
            "target_audience": "A detailed description of the ideal customer. Who are they? What do they desire? What problems from the histories does this solve for them?",
            "marketing_plan": {{
                "content_pillars": ["Pillar 1: e.g., 'Answering 'how-to' questions from Reddit'", "Pillar 2: e.g., 'Showcasing alignment with news trends'"],
                "promotion_channels": ["Channel 1: e.g., 'SEO targeting rising queries'", "Channel 2: e.g., 'Pinterest for visual discovery'"],
                "unique_selling_proposition": "What makes this venture unique and powerful? The one message to rule them all."
            }},
            "sourcing_and_operations": "Initial counsel on how to source the product or build the service. Should they look to AliExpress, find local artisans, or develop software?",
            "worst_case_monthly_profit_omen": {{
                "scenario": "A realistic, worst-case financial vision for one month of operation. Be conservative.",
                "estimated_revenue": {{"calculation": "e.g., 10 sales @ $50/sale", "value": 500}},
                "estimated_costs": [
                    {{"item": "Cost of Goods (for 10 sales)", "calculation": "e.g., 10 units @ $15/unit", "value": 150}},
                    {{"item": "Marketing Spend", "calculation": "e.g., A modest starting ad budget", "value": 100}},
                    {{"item": "Platform Fees (approx. 10%)", "calculation": "e.g., 10% of revenue", "value": 50}}
                ],
                "prophesied_profit": {{"calculation": "Revenue - All Costs", "value": 200}},
                "counsel": "Your wisdom on this financial omen. 'This is a starting point. Focus on increasing sales volume and managing costs to improve this fate.'"
            }},
            "first_three_steps": [
                "Step 1: Your first step on this path is to...",
                "Step 2: Next, you must forge...",
                "Step 3: Then, you will announce your arrival by..."
            ]
        }}
        """
        
        return await get_prophecy_from_oracle(self.model, prompt)
--- END OF FILE backend/stacks/new_ventures_stack.py ---