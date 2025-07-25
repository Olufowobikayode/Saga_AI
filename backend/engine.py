# --- START OF THE FULL AND ABSOLUTE SCROLL: backend/engine.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import iso3166
import uuid

# --- The great power of the single Oracle is no longer summoned here. ---
# import google.generativeai as genai --- THIS LINE IS BANISHED ---

# --- Import all specialist knowledge sources (The Seers) ---
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle

# --- Import the great Halls of Wisdom (The Stacks) ---
from backend.stacks.new_ventures_stack import NewVenturesStack
from backend.stacks.content_saga_stack import ContentSagaStack
from backend.stacks.grand_strategy_stack import GrandStrategyStack
from backend.stacks.marketing_saga_stack import MarketingSagaStack
from backend.stacks.pod_stack import PODSagaStack
from backend.stacks.commerce_saga_stack import CommerceSagaStack

logger = logging.getLogger(__name__)

class SagaEngine:
    """
    The SagaEngine is the heart of the application. It now orchestrates the
    gathering of intelligence from its seers, knowing that the Stacks will

    draw their prophetic voice from the great Oracle Constellation.
    """
    def __init__(self, gemini_api_key: str, ip_geolocation_api_key: Optional[str] = None):
        """
        The rite of awakening. The single gemini_api_key is accepted but no longer used
        to configure a single Oracle. I now trust the Constellation.
        """
        logger.info("The SagaEngine awakens... The Constellation of Oracles is now my voice.")

        # --- THESE SACRED LINES ARE BANISHED ---
        # genai.configure(api_key=gemini_api_key)
        # self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        # self.gemini_api_key = gemini_api_key
        # --- END OF BANISHMENT ---

        self.ip_geolocation_api_key = ip_geolocation_api_key

        seers = {
            'community_seer': CommunitySaga(),
            'trend_scraper': TrendScraper(),
            'keyword_rune_keeper': KeywordRuneKeeper(),
            'marketplace_oracle': GlobalMarketplaceOracle()
        }

        # --- THE GREAT DECREE OF SIMPLIFICATION ---
        # The Stacks are no longer imbued with a single model. They will seek
        # their own counsel from the Constellation when the time is right.
        self.grand_strategy_stack = GrandStrategyStack(**seers)
        self.content_saga_stack = ContentSagaStack(**seers)
        self.new_ventures_stack = NewVenturesStack(**seers)
        self.marketing_saga_stack = MarketingSagaStack(**seers)
        self.pod_saga_stack = PODSagaStack(**seers)
        self.commerce_saga_stack = CommerceSagaStack(**seers)
        
        self.strategy_session_cache = {}
        logger.info("Saga is now fully conscious and ready to share her wisdom.")

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

    async def _resolve_country_context(self, user_ip_address: Optional[str], target_country_name: Optional[str]) -> Dict:
        """A rite to determine the mortal realm of the prophecy."""
        country_name, country_code, is_global = "Global", None, True
        if target_country_name and target_country_name.lower() != "global":
            try:
                country_entry = iso3166.countries.get(target_country_name)
                country_name, country_code, is_global = country_entry.name, country_entry.alpha2, False
            except KeyError:
                logger.warning(f"Realm '{target_country_name}' not in scrolls. Prophecy will be global.")
        return {"country_name": country_name, "country_code": country_code, "is_global": is_global}

    def _get_session_or_raise(self, session_id: str) -> Dict:
        """A rite to recall the memory of a previous divination within a seeker's journey."""
        session_data = self.strategy_session_cache.get(session_id)
        if not session_data:
            raise ValueError("Invalid session ID. A prophecy must be divined first.")
        return session_data

    # --- STRATEGIC & VENTURE PROPHECIES ---
    async def prophesy_grand_strategy(self, **kwargs) -> Dict:
        """The First Great Prophecy: The Grand Strategy."""
        logger.info(f"SAGA ENGINE: Calling Commander Stack for: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(None, kwargs.get("target_country_name"))
        strategy_data = await self.grand_strategy_stack.prophesy(
            interest=kwargs.get("interest"),
            country_code=country_context["country_code"],
            country_name=country_context["country_name"],
            user_tone_instruction=user_tone_instruction,
            asset_info=kwargs.get("asset_info")
        )
        strategy_session_id = str(uuid.uuid4())
        self.strategy_session_cache[strategy_session_id] = strategy_data
        return {"strategy_session_id": strategy_session_id, "prophecy": strategy_data.get("prophecy")}

    async def prophesy_new_venture_visions(self, **kwargs) -> Dict:
        """The Prophecy of Beginnings: Divining new ventures."""
        logger.info(f"SAGA ENGINE: Calling New Ventures Stack for: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(None, kwargs.get("target_country_name"))
        venture_data = await self.new_ventures_stack.prophesy_initial_visions(
            interest=kwargs.get("interest"),
            country_code=country_context["country_code"],
            country_name=country_context["country_name"],
            user_tone_instruction=user_tone_instruction,
            venture_brief=kwargs.get("venture_brief")
        )
        venture_session_id = str(uuid.uuid4())
        self.strategy_session_cache[venture_session_id] = venture_data
        return {"venture_session_id": venture_session_id, "visions": venture_data.get("initial_visions")}

    async def prophesy_venture_blueprint(self, venture_session_id: str, chosen_vision: Dict[str, Any]) -> Dict[str, Any]:
        """The Prophecy of Forging: Creating a full business blueprint."""
        logger.info(f"VENTURE BLUEPRINT ENGINE: Authorized by session {venture_session_id} for vision '{chosen_vision.get('title')}'")
        session_data = self._get_session_or_raise(venture_session_id)
        
        retrieved_histories = session_data.get("retrieved_histories_for_blueprint", {})
        user_tone_instruction = session_data.get("user_tone_instruction", "")
        country_name = session_data.get("country_name", "Global")

        return await self.new_ventures_stack.prophesy_detailed_blueprint(
            chosen_vision=chosen_vision,
            retrieved_histories=retrieved_histories,
            user_tone_instruction=user_tone_instruction,
            country_name=country_name
        )

    # --- TACTICAL PROPHECIES ---
    async def prophesy_marketing_angles(self, **kwargs) -> Dict:
        """The Skald's Prophecy: Forging marketing angles."""
        logger.info(f"MARKETING ANGLES ENGINE: Generating marketing angles...")
        angles_prophecy = await self.marketing_saga_stack.prophesy_marketing_angles(**kwargs)
        marketing_session_id = str(uuid.uuid4())
        self.strategy_session_cache[marketing_session_id] = angles_prophecy
        return {"marketing_session_id": marketing_session_id, "marketing_angles": angles_prophecy.get("marketing_angles", [])}

    async def prophesy_marketing_asset(self, marketing_session_id: str, angle_id: str, **kwargs) -> Dict[str, Any]:
        """The Skald's Final Verse: Creating a complete marketing asset."""
        logger.info(f"MARKETING ASSET ENGINE: Authorized by session {marketing_session_id} for angle {angle_id}")
        session_data = self._get_session_or_raise(marketing_session_id)
        try:
            chosen_angle = next(a for a in session_data.get("marketing_angles", []) if a["angle_id"] == angle_id)
        except StopIteration:
            raise ValueError("The selected angle_id was not found in the prophecy.")
        full_angle_data = {**session_data, **chosen_angle, **kwargs}
        return await self.marketing_saga_stack.prophesy_final_asset(full_angle_data)

    async def prophesy_pod_opportunities(self, **kwargs) -> Dict[str, Any]:
        """The Artisan's Prophecy: Divining print-on-demand concepts."""
        logger.info(f"POD OPPORTUNITY ENGINE: Divining concepts...")
        opportunities_prophecy = await self.pod_saga_stack.prophesy_pod_opportunities(**kwargs)
        pod_session_id = str(uuid.uuid4())
        self.strategy_session_cache[pod_session_id] = opportunities_prophecy
        return {"pod_session_id": pod_session_id, "design_concepts": opportunities_prophecy.get("design_concepts", [])}

    async def prophesy_pod_design_package(self, pod_session_id: str, concept_id: str) -> Dict[str, Any]:
        """The Artisan's Masterwork: Forging a full design and listing package."""
        logger.info(f"POD DESIGN PACKAGE ENGINE: Authorized by session {pod_session_id} for concept {concept_id}")
        session_data = self._get_session_or_raise(pod_session_id)
        try:
            chosen_concept = next(c for c in session_data.get("design_concepts", []) if c["concept_id"] == concept_id)
        except StopIteration:
            raise ValueError("The selected concept_id was not found in the prophecy.")
        full_opportunity_data = {**session_data, **chosen_concept}
        return await self.pod_saga_stack.prophesy_pod_design_package(full_opportunity_data)

    async def prophesy_commerce_saga(self, prophecy_type: str, **kwargs) -> Dict[str, Any]:
        """The Merchant's Prophecy: Divining the flow of coin and commerce."""
        logger.info(f"COMMERCE SAGA ENGINE: Invoking prophecy of '{prophecy_type}'...")
        if prophecy_type == "Commerce Audit":
            return await self.commerce_saga_stack.prophesy_commerce_audit(**kwargs)
        elif prophecy_type == "Arbitrage Paths":
            return await self.commerce_saga_stack.prophesy_arbitrage_paths(**kwargs)
        elif prophecy_type == "Social Selling Saga":
            return await self.commerce_saga_stack.prophesy_social_selling_saga(**kwargs)
        elif prophecy_type == "Product Route":
            return await self.commerce_saga_stack.prophesy_product_route(**kwargs)
        else:
            raise ValueError(f"Unknown Commerce Saga prophecy type: '{prophecy_type}'")
# --- END OF THE FULL AND ABSOLUTE SCROLL: backend/engine.py ---