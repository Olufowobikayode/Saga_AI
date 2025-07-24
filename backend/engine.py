# --- START OF FILE backend/engine.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import aiohttp
import iso3166
import uuid

import google.generativeai as genai

from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle
from backend.stacks.new_ventures_stack import NewVenturesStack
from backend.stacks.content_saga_stack import ContentSagaStack
from backend.stacks.grand_strategy_stack import GrandStrategyStack
from backend.stacks.marketing_saga_stack import MarketingSagaStack
from backend.stacks.pod_stack import PODSagaStack
from backend.stacks.commerce_saga_stack import CommerceSagaStack

logger = logging.getLogger(__name__)

class SagaEngine:
    def __init__(self, gemini_api_key: str, ip_geolocation_api_key: Optional[str] = None):
        logger.info("The SagaEngine awakens...")
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        self.gemini_api_key = gemini_api_key
        self.ip_geolocation_api_key = ip_geolocation_api_key
        self.community_seer = CommunitySaga()
        self.trend_scraper = TrendScraper()
        self.keyword_rune_keeper = KeywordRuneKeeper()
        self.marketplace_oracle = GlobalMarketplaceOracle()
        seers = {'community_seer': self.community_seer, 'trend_scraper': self.trend_scraper, 'keyword_rune_keeper': self.keyword_rune_keeper, 'marketplace_oracle': self.marketplace_oracle}
        self.grand_strategy_stack = GrandStrategyStack(model=self.model, **seers)
        self.content_saga_stack = ContentSagaStack(model=self.model, **seers)
        self.new_ventures_stack = NewVenturesStack(model=self.model, **seers)
        self.marketing_saga_stack = MarketingSagaStack(model=self.model, **seers)
        self.pod_saga_stack = PODSagaStack(model=self.model, **seers)
        self.commerce_saga_stack = CommerceSagaStack(model=self.model, **seers)
        self.strategy_session_cache = {}
        logger.info("Saga is now fully conscious.")

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        user_input_content_for_ai = None
        if user_content_text: user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self.marketplace_oracle.read_user_store_scroll(user_content_url)
            if scraped_content: user_input_content_for_ai = scraped_content
        if user_input_content_for_ai:
            return f"**THE USER'S WRITING STYLE:**\nAnalyze the tone and style of the following text. You MUST adopt this voice.\n---\n{user_input_content_for_ai[:10000]}\n---"
        return "You shall speak with the direct, wise, and prophetic voice of Saga."

    async def _resolve_country_context(self, user_ip_address: Optional[str], target_country_name: Optional[str]) -> Dict:
        country_name, country_code, is_global = "Global", None, True
        if target_country_name and target_country_name.lower() != "global":
            try:
                country_entry = iso3166.countries.get(target_country_name)
                country_name, country_code, is_global = country_entry.name, country_entry.alpha2, False
            except KeyError: logger.warning(f"Realm '{target_country_name}' not in scrolls.")
        return {"country_name": country_name, "country_code": country_code, "is_global": is_global}

    def _get_session_or_raise(self, session_id: str) -> Dict:
        if not (session_data := self.strategy_session_cache.get(session_id)):
            raise ValueError("Invalid session ID.")
        return session_data

    async def prophesy_grand_strategy(self, **kwargs) -> Dict:
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        strategy_data = await self.grand_strategy_stack.prophesy(
            interest=kwargs.get("interest"), country_code=country_context["country_code"],
            country_name=country_context["country_name"], user_tone_instruction=user_tone_instruction,
            asset_info=kwargs.get("asset_info")
        )
        strategy_session_id = str(uuid.uuid4())
        self.strategy_session_cache[strategy_session_id] = strategy_data
        return {"strategy_session_id": strategy_session_id, "prophecy": strategy_data.get("prophecy")}

    async def prophesy_new_venture_visions(self, **kwargs) -> Dict:
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        venture_data = await self.new_ventures_stack.prophesy_initial_visions(
            interest=kwargs.get("interest"), country_code=country_context["country_code"],
            country_name=country_context["country_name"], user_tone_instruction=user_tone_instruction,
            venture_brief=kwargs.get("venture_brief")
        )
        venture_session_id = str(uuid.uuid4())
        self.strategy_session_cache[venture_session_id] = venture_data
        return {"venture_session_id": venture_session_id, "visions": venture_data.get("initial_visions")}

    async def prophesy_venture_blueprint(self, venture_session_id: str, vision_id: str) -> Dict[str, Any]:
        session_data = self._get_session_or_raise(venture_session_id)
        try:
            chosen_vision = next(v for v in session_data.get("initial_visions", []) if v["prophecy_id"] == vision_id)
        except StopIteration: raise ValueError("Vision ID not found.")
        return await self.new_ventures_stack.prophesy_detailed_blueprint(
            chosen_vision=chosen_vision, retrieved_histories=session_data.get("retrieved_histories_for_blueprint", {}),
            user_tone_instruction=session_data.get("user_tone_instruction", ""), country_name=session_data.get("country_name", "Global")
        )

    async def prophesy_marketing_angles(self, **kwargs) -> Dict:
        angles_prophecy = await self.marketing_saga_stack.prophesy_marketing_angles(**kwargs)
        marketing_session_id = str(uuid.uuid4())
        self.strategy_session_cache[marketing_session_id] = angles_prophecy
        return {"marketing_session_id": marketing_session_id, "marketing_angles": angles_prophecy.get("marketing_angles", [])}

    async def prophesy_marketing_asset(self, marketing_session_id: str, angle_id: str, **kwargs) -> Dict[str, Any]:
        session_data = self._get_session_or_raise(marketing_session_id)
        try:
            chosen_angle = next(a for a in session_data.get("marketing_angles", []) if a["angle_id"] == angle_id)
        except StopIteration: raise ValueError("Angle ID not found.")
        full_angle_data = {**session_data, **chosen_angle, **kwargs}
        return await self.marketing_saga_stack.prophesy_final_asset(full_angle_data)

    async def prophesy_pod_opportunities(self, niche_interest: str) -> Dict[str, Any]:
        opportunities_prophecy = await self.pod_saga_stack.prophesy_pod_opportunities(niche_interest)
        pod_session_id = str(uuid.uuid4())
        self.strategy_session_cache[pod_session_id] = opportunities_prophecy
        return {"pod_session_id": pod_session_id, "design_concepts": opportunities_prophecy.get("design_concepts", [])}

    async def prophesy_pod_design_package(self, pod_session_id: str, concept_id: str) -> Dict[str, Any]:
        session_data = self._get_session_or_raise(pod_session_id)
        try:
            chosen_concept = next(c for c in session_data.get("design_concepts", []) if c["concept_id"] == concept_id)
        except StopIteration: raise ValueError("Concept ID not found.")
        full_opportunity_data = {**session_data, **chosen_concept}
        return await self.pod_saga_stack.prophesy_pod_design_package(full_opportunity_data)

    async def prophesy_commerce_saga(self, prophecy_type: str, **kwargs) -> Dict[str, Any]:
        if prophecy_type == "Commerce Audit": return await self.commerce_saga_stack.prophesy_commerce_audit(**kwargs)
        elif prophecy_type == "Arbitrage Paths": return await self.commerce_saga_stack.prophesy_arbitrage_paths(**kwargs)
        elif prophecy_type == "Social Selling Saga": return await self.commerce_saga_stack.prophesy_social_selling_saga(**kwargs)
        elif prophecy_type == "Product Route": return await self.commerce_saga_stack.prophesy_product_route(**kwargs)
        else: raise ValueError(f"Unknown Commerce Saga: '{prophecy_type}'")
# --- END OF FILE backend/engine.py ---