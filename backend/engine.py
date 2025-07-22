--- START OF FILE backend/engine.py ---
import asyncio
import logging
import json
from typing --- START OF FILE backend/engine.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import aiohttp
import iso3166
import uuid

import google.generativeai as genai

# --- Import all specialist knowledge sources ---
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.ecommerce_audit_analyzer import EcommerceAuditAnalyzer
from backend.price_arbitrage_finder import PriceArbitrageFinder
from backend.social_selling_strategist import SocialSellingStrategist
from backend.product_route_suggester import ProductRouteSuggester
from backend.utils import get_prophecy_from_oracle

# --- Import the STACKS ---
from backend.stacks.new_ventures_stack import NewVenturesStack
from backend.stacks.content_saga_stack import ContentSagaStack
from backend.stacks.grand_strategy_stack import GrandStrategyStack
from backend.stacks.marketing_saga_stack import MarketingSagaStack
from backend.stacks.pod_stack import PODSagaStack

logger = logging.getLogger(__name__)

class SagaEngine:
    """
    The SagaEngine is the heart of the application, the digital embodiment
    of the Norse goddess of wisdom. It orchestrates the gathering of intelligence
    from its assembled seers and commands its specialist stacks to forge prophecies
    for the user.
    """
    def __init__(self, gemini_api_key: str, ip_geolocation_api_key: Optional[str] = None):
        """
        Initializes the SagaEngine, awakening all her seers and oracles.
        """
        logger.info("The SagaEngine awakens... Summoning all sources of wisdom.")
        
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.gemini_api_key = gemini_api_key
        self.ip_geolocation_api_key = ip_geolocation_api_key

        # --- Instantiate all knowledge sources (Seers and Oracles) ---
        self.community_seer = CommunitySaga()
        self.trend_scraper = TrendScraper()
        self.keyword_rune_keeper = KeywordRuneKeeper()
        self.marketplace_oracle = GlobalMarketplaceOracle()
        
        # --- Instantiate all specialist stacks and analyzers ---
        self.grand_strategy_stack = GrandStrategyStack(
            model=self.model,
            keyword_rune_keeper=self.keyword_rune_keeper,
            community_seer=self.community_seer,
            trend_scraper=self.trend_scraper
        )
        self.content_saga_stack = ContentSagaStack(
            model=self.model,
            keyword_rune_keeper=self.keyword_rune_keeper,
            community_seer=self.community_seer
        )
        self.new_ventures_stack = NewVenturesStack(
            model=self.model,
            keyword_rune_keeper=self.keyword_rune_keeper,
            community_seer=self.community_seer,
            trend_scraper=self.trend_scraper,
            marketplace_oracle=self.marketplace_oracle
        )
        self.marketing_saga_stack = MarketingSagaStack(
            model=self.model,
            community_seer=self.community_seer
        )
        self.pod_saga_stack = PODSagaStack(
            model=self.model,
            community_seer=self.community_seer,
            keyword_rune_keeper=self.keyword_rune_keeper,
            marketplace_oracle=self.marketplace_oracle
        )
        self.audit_analyzer = EcommerceAuditAnalyzer(self.gemini_api_key, self.marketplace_oracle)
        self.price_arbitrage_finder = PriceArbitrageFinder(self.gemini_api_key, self.marketplace_oracle)
        self.social_selling_strategist = SocialSellingStrategist(self.gemini_api_key, self.marketplace_oracle)
        self.product_route_suggester = ProductRouteSuggester(self.gemini_api_key, self.marketplace_oracle)
        
        self.strategy_session_cache = {}

        logger.info("Saga is now fully conscious and ready to share her wisdom.")

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        user_input_content_for_ai = None
        if user_content_text: user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self.marketplace_oracle.read_user_store_scroll(user_content_url)
            if scraped_content: user_input_content_for_ai = scraped_content
        if user_input_content_for_ai:
            return f"**THE USER'S OWN SAGA (Their Writing Style):**\nAnalyze the tone, style, and vocabulary of the following text. When you weave your prophecy, you MUST adopt this voice so the wisdom feels as if it comes from within themselves.\n---\n{user_input_content_for_ai}\n---"
        return "You shall speak with the direct, wise, and prophetic voice of Saga."

    async def _resolve_country_context(self, user_ip_address: Optional[str], target_country_name: Optional[str]) -> Dict:
        country_name, country_code, is_global = "Global", None, True
        if target_country_name and target_country_name.lower() != "global":
            try:
                country_entry = iso3166.countries.get(target_country_name)
                country_name, country_code, is_global = country_entry.name, country_entry.alpha2, False
            except KeyError:
                logger.warning(f"Realm '{target_country_name}' not in scrolls. Prophecy will be global.")
        return {"country_name": country_name, "country_code": country_code, "is_global": is_global}

    def _get_session_or_raise(self, session_id: str) -> Dict:
        """Helper to authorize and retrieve session data or raise an error."""
        session_data = self.strategy_session_cache.get(session_id)
        if not session_data:
            raise ValueError("Invalid session ID. A prophecy must be divined first.")
        return session_data

    # --- STRATEGIC & VENTURE PROPHECIES (The Starting Points) ---

    async def prophesy_grand_strategy(self, **kwargs) -> Dict:
        """Calls the Commander Stack to forge a master plan and returns a session key."""
        logger.info(f"SAGA ENGINE: Calling Commander Stack for: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))

        strategy_data = await self.grand_strategy_stack.prophesy(
            interest=kwargs.get("interest"),
            country_code=country_context["country_code"],
            country_name=country_context["country_name"],
            user_tone_instruction=user_tone_instruction
        )
        
        strategy_session_id = str(uuid.uuid4())
        self.strategy_session_cache[strategy_session_id] = {
            "grand_strategy": strategy_data,
            "user_tone_instruction": user_tone_instruction,
            "country_context": country_context
        }
        
        return {"strategy_session_id": strategy_session_id, "prophecy": strategy_data.get("prophecy")}

    async def prophesy_new_venture_visions(self, **kwargs) -> Dict:
        """Calls the New Ventures Stack to generate 10 business ideas."""
        logger.info(f"SAGA ENGINE: Calling New Ventures Stack for: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))

        venture_data = await self.new_ventures_stack.prophesy_initial_visions(
            interest=kwargs.get("interest"),
            country_code=country_context["country_code"],
            country_name=country_context["country_name"],
            user_tone_instruction=user_tone_instruction
        )
        
        venture_session_id = str(uuid.uuid4())
        self.strategy_session_cache[venture_session_id] = venture_data
        
        return {"venture_session_id": venture_session_id, "visions": venture_data.get("initial_visions")}

    # --- TACTICAL PROPHECIES (Commerce, Content, Marketing, POD) ---

    async def prophesy_ecommerce_audit(self, strategy_session_id: str, **kwargs) -> Dict:
        logger.info(f"ECOMMERCE AUDIT ENGINE: Authorized by session {strategy_session_id}")
        session_data = self._get_session_or_raise(strategy_session_id)
        request_args = {"user_tone_instruction": session_data["user_tone_instruction"], **session_data.get("country_context", {}), **kwargs}
        return await self.audit_analyzer.run_audit_and_strategy(**request_args)

    async def prophesy_price_arbitrage(self, strategy_session_id: str, **kwargs) -> Dict:
        logger.info(f"PRICE ARBITRAGE ENGINE: Authorized by session {strategy_session_id}")
        session_data = self._get_session_or_raise(strategy_session_id)
        request_args = {"user_tone_instruction": session_data["user_tone_instruction"], "country_name_for_ai": session_data.get("country_context", {}).get("country_name"), **kwargs}
        return await self.price_arbitrage_finder.divine_arbitrage_paths(**request_args)

    async def prophesy_social_selling(self, strategy_session_id: str, **kwargs) -> Dict:
        logger.info(f"SOCIAL SELLING ENGINE: Authorized by session {strategy_session_id}")
        session_data = self._get_session_or_raise(strategy_session_id)
        request_args = {"user_tone_instruction": session_data["user_tone_instruction"], "target_country_name": session_data.get("country_context", {}).get("country_name"), **kwargs}
        return await self.social_selling_strategist.devise_social_selling_saga(**request_args)

    async def prophesy_product_route(self, strategy_session_id: str, **kwargs) -> Dict:
        logger.info(f"PRODUCT ROUTE ENGINE: Authorized by session {strategy_session_id}")
        session_data = self._get_session_or_raise(strategy_session_id)
        request_args = {"user_tone_instruction": session_data["user_tone_instruction"], "target_country_name": session_data.get("country_context", {}).get("country_name"), **kwargs}
        return await self.product_route_suggester.prophesy_product_route(**request_args)

    async def prophesy_marketing_angles(self, **kwargs) -> Dict:
        """Phase 1 of Marketing Saga: Researches and generates strategic angles."""
        logger.info(f"MARKETING ANGLES ENGINE: Generating marketing angles...")
        angles_prophecy = await self.marketing_saga_stack.prophesy_marketing_angles(**kwargs)
        marketing_session_id = str(uuid.uuid4())
        self.strategy_session_cache[marketing_session_id] = angles_prophecy
        return {"marketing_session_id": marketing_session_id, "marketing_angles": angles_prophecy.get("marketing_angles", [])}

    async def prophesy_marketing_asset(self, marketing_session_id: str, angle_id: str) -> Dict[str, Any]:
        """Phase 2 of Marketing Saga: Generates a final, specific asset from a chosen angle."""
        logger.info(f"MARKETING ASSET ENGINE: Authorized by session {marketing_session_id} for angle {angle_id}")
        session_data = self._get_session_or_raise(marketing_session_id)
        try:
            chosen_angle = next(a for a in session_data.get("marketing_angles", []) if a["angle_id"] == angle_id)
        except StopIteration:
            raise ValueError("The selected angle_id was not found in the prophecy.")

        full_angle_data = {**session_data, **chosen_angle}
        asset_type = session_data.get("asset_type")

        if asset_type == "Ad Copy": return await self.marketing_saga_stack.prophesy_ad_copy_from_angle(full_angle_data)
        elif asset_type in ["Landing Page", "Funnel Page"]: return await self.marketing_saga_stack.prophesy_page_html_from_angle(full_angle_data)
        elif asset_type in ["Affiliate Copy", "Email Copy"]: return await self.marketing_saga_stack.prophesy_affiliate_or_email_copy_from_angle(full_angle_data)
        else: raise ValueError(f"Unknown asset type '{asset_type}' requested.")

    async def prophesy_pod_opportunities(self, niche_interest: str) -> Dict[str, Any]:
        """Phase 1 of POD Saga: Researches a niche and generates strategic Design Concept cards."""
        logger.info(f"POD OPPORTUNITY ENGINE: Divining concepts for niche '{niche_interest}'...")
        opportunities_prophecy = await self.pod_saga_stack.prophesy_pod_opportunities(niche_interest)
        pod_session_id = str(uuid.uuid4())
        self.strategy_session_cache[pod_session_id] = opportunities_prophecy
        return {"pod_session_id": pod_session_id, "design_concepts": opportunities_prophecy.get("design_concepts", [])}

    async def prophesy_pod_design_package(self, pod_session_id: str, concept_id: str) -> Dict[str, Any]:
        """Phase 2 of POD Saga: Generates a final, specific design and listing package."""
        logger.info(f"POD DESIGN PACKAGE ENGINE: Authorized by session {pod_session_id} for concept {concept_id}")
        session_data = self._get_session_or_raise(pod_session_id)
        try:
            chosen_concept = next(c for c in session_data.get("design_concepts", []) if c["concept_id"] == concept_id)
        except StopIteration:
            raise ValueError("The selected concept_id was not found in the prophecy.")

        full_opportunity_data = {**session_data, **chosen_concept}
        return await self.pod_saga_stack.prophesy_pod_design_package(full_opportunity_data)

--- END OF FILE backend/engine.py --- Dict, Any, Optional, List
import aiohttp
import iso3166
import uuid

import google.generativeai as genai

# --- Import all specialist knowledge sources ---
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.ecommerce_audit_analyzer import EcommerceAuditAnalyzer
from backend.price_arbitrage_finder import PriceArbitrageFinder
from backend.social_selling_strategist import SocialSellingStrategist
from backend.product_route_suggester import ProductRouteSuggester
from backend.utils import get_prophecy_from_oracle

# --- Import the STACKS ---
from backend.stacks.new_ventures_stack import NewVenturesStack
from backend.stacks.content_saga_stack import ContentSagaStack
from backend.stacks.grand_strategy_stack import GrandStrategyStack
from backend.stacks.marketing_saga_stack import MarketingSagaStack

logger = logging.getLogger(__name__)

class SagaEngine:
    """
    The SagaEngine is the heart of the application, the digital embodiment
    of the Norse goddess of wisdom. It orchestrates the gathering of intelligence
    from its assembled seers and commands its specialist stacks to forge prophecies
    for the user.
    """
    def __init__(self, gemini_api_key: str, ip_geolocation_api_key: Optional[str] = None):
        """
        Initializes the SagaEngine, awakening all her seers and oracles.
        """
        logger.info("The SagaEngine awakens... Summoning all sources of wisdom.")
        
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.gemini_api_key = gemini_api_key
        self.ip_geolocation_api_key = ip_geolocation_api_key

        # --- Instantiate all knowledge sources (Seers and Oracles) ---
        self.community_seer = CommunitySaga()
        self.trend_scraper = TrendScraper()
        self.keyword_rune_keeper = KeywordRuneKeeper()
        self.marketplace_oracle = GlobalMarketplaceOracle()
        
        # --- Instantiate all specialist stacks and analyzers ---
        self.grand_strategy_stack = GrandStrategyStack(
            model=self.model,
            keyword_rune_keeper=self.keyword_rune_keeper,
            community_seer=self.community_seer,
            trend_scraper=self.trend_scraper
        )
        self.content_saga_stack = ContentSagaStack(
            model=self.model,
            keyword_rune_keeper=self.keyword_rune_keeper,
            community_seer=self.community_seer
        )
        self.new_ventures_stack = NewVenturesStack(
            model=self.model,
            keyword_rune_keeper=self.keyword_rune_keeper,
            community_seer=self.community_seer,
            trend_scraper=self.trend_scraper,
            marketplace_oracle=self.marketplace_oracle
        )
        self.marketing_saga_stack = MarketingSagaStack(
            model=self.model,
            community_seer=self.community_seer
        )
        self.audit_analyzer = EcommerceAuditAnalyzer(self.gemini_api_key, self.marketplace_oracle)
        self.price_arbitrage_finder = PriceArbitrageFinder(self.gemini_api_key, self.marketplace_oracle)
        self.social_selling_strategist = SocialSellingStrategist(self.gemini_api_key, self.marketplace_oracle)
        self.product_route_suggester = ProductRouteSuggester(self.gemini_api_key, self.marketplace_oracle)
        
        self.strategy_session_cache = {}

        logger.info("Saga is now fully conscious and ready to share her wisdom.")

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        user_input_content_for_ai = None
        if user_content_text: user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self.marketplace_oracle.read_user_store_scroll(user_content_url)
            if scraped_content: user_input_content_for_ai = scraped_content
        if user_input_content_for_ai:
            return f"**THE USER'S OWN SAGA (Their Writing Style):**\nAnalyze the tone, style, and vocabulary of the following text. When you weave your prophecy, you MUST adopt this voice so the wisdom feels as if it comes from within themselves.\n---\n{user_input_content_for_ai}\n---"
        return "You shall speak with the direct, wise, and prophetic voice of Saga."

    async def _resolve_country_context(self, user_ip_address: Optional[str], target_country_name: Optional[str]) -> Dict:
        country_name, country_code, is_global = "Global", None, True
        if target_country_name and target_country_name.lower() != "global":
            try:
                country_entry = iso3166.countries.get(target_country_name)
                country_name, country_code, is_global = country_entry.name, country_entry.alpha2, False
            except KeyError:
                logger.warning(f"Realm '{target_country_name}' not in scrolls. Prophecy will be global.")
        return {"country_name": country_name, "country_code": country_code, "is_global": is_global}

    def _get_session_or_raise(self, session_id: str) -> Dict:
        """Helper to authorize and retrieve session data or raise an error."""
        session_data = self.strategy_session_cache.get(session_id)
        if not session_data:
            raise ValueError("Invalid session ID. A prophecy must be divined first.")
        return session_data

    # --- STRATEGIC & VENTURE PROPHECIES (The Starting Points) ---

    async def prophesy_grand_strategy(self, **kwargs) -> Dict:
        """Calls the Commander Stack to forge a master plan and returns a session key."""
        logger.info(f"SAGA ENGINE: Calling Commander Stack for: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))

        strategy_data = await self.grand_strategy_stack.prophesy(
            interest=kwargs.get("interest"),
            country_code=country_context["country_code"],
            country_name=country_context["country_name"],
            user_tone_instruction=user_tone_instruction
        )
        
        strategy_session_id = str(uuid.uuid4())
        self.strategy_session_cache[strategy_session_id] = {
            "grand_strategy": strategy_data,
            "user_tone_instruction": user_tone_instruction,
            "country_context": country_context
        }
        
        return {"strategy_session_id": strategy_session_id, "prophecy": strategy_data.get("prophecy")}

    async def prophesy_new_venture_visions(self, **kwargs) -> Dict:
        """Calls the New Ventures Stack to generate 10 business ideas."""
        logger.info(f"SAGA ENGINE: Calling New Ventures Stack for: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))

        venture_data = await self.new_ventures_stack.prophesy_initial_visions(
            interest=kwargs.get("interest"),
            country_code=country_context["country_code"],
            country_name=country_context["country_name"],
            user_tone_instruction=user_tone_instruction
        )
        
        venture_session_id = str(uuid.uuid4())
        self.strategy_session_cache[venture_session_id] = venture_data
        
        return {"venture_session_id": venture_session_id, "visions": venture_data.get("initial_visions")}

    # --- TACTICAL PROPHECIES (Commerce, Content, Marketing) ---

    async def prophesy_ecommerce_audit(self, strategy_session_id: str, **kwargs) -> Dict:
        logger.info(f"ECOMMERCE AUDIT ENGINE: Authorized by session {strategy_session_id}")
        session_data = self._get_session_or_raise(strategy_session_id)
        request_args = {"user_tone_instruction": session_data["user_tone_instruction"], **session_data.get("country_context", {}), **kwargs}
        return await self.audit_analyzer.run_audit_and_strategy(**request_args)

    async def prophesy_price_arbitrage(self, strategy_session_id: str, **kwargs) -> Dict:
        logger.info(f"PRICE ARBITRAGE ENGINE: Authorized by session {strategy_session_id}")
        session_data = self._get_session_or_raise(strategy_session_id)
        request_args = {"user_tone_instruction": session_data["user_tone_instruction"], "country_name_for_ai": session_data.get("country_context", {}).get("country_name"), **kwargs}
        return await self.price_arbitrage_finder.divine_arbitrage_paths(**request_args)

    async def prophesy_social_selling(self, strategy_session_id: str, **kwargs) -> Dict:
        logger.info(f"SOCIAL SELLING ENGINE: Authorized by session {strategy_session_id}")
        session_data = self._get_session_or_raise(strategy_session_id)
        request_args = {"user_tone_instruction": session_data["user_tone_instruction"], "target_country_name": session_data.get("country_context", {}).get("country_name"), **kwargs}
        return await self.social_selling_strategist.devise_social_selling_saga(**request_args)

    async def prophesy_product_route(self, strategy_session_id: str, **kwargs) -> Dict:
        logger.info(f"PRODUCT ROUTE ENGINE: Authorized by session {strategy_session_id}")
        session_data = self._get_session_or_raise(strategy_session_id)
        request_args = {"user_tone_instruction": session_data["user_tone_instruction"], "target_country_name": session_data.get("country_context", {}).get("country_name"), **kwargs}
        return await self.product_route_suggester.prophesy_product_route(**request_args)

    async def prophesy_marketing_angles(self, **kwargs) -> Dict:
        """Phase 1 of Marketing Saga: Researches and generates strategic angles."""
        logger.info(f"MARKETING ANGLES ENGINE: Generating marketing angles...")
        # This prophecy is multi-stage, so we must cache the results for Phase 2.
        angles_prophecy = await self.marketing_saga_stack.prophesy_marketing_angles(**kwargs)
        
        marketing_session_id = str(uuid.uuid4())
        self.strategy_session_cache[marketing_session_id] = angles_prophecy
        
        # We only return the 'cards' to the user for them to choose from.
        return {"marketing_session_id": marketing_session_id, "marketing_angles": angles_prophecy.get("marketing_angles", [])}

    async def prophesy_marketing_asset(self, marketing_session_id: str, angle_id: str) -> Dict[str, Any]:
        """Phase 2 of Marketing Saga: Generates a final, specific asset from a chosen angle."""
        logger.info(f"MARKETING ASSET ENGINE: Authorized by session {marketing_session_id} for angle {angle_id}")
        session_data = self._get_session_or_raise(marketing_session_id)
        
        try:
            chosen_angle = next(a for a in session_data.get("marketing_angles", []) if a["angle_id"] == angle_id)
        except StopIteration:
            raise ValueError("The selected angle_id was not found in the prophecy.")

        full_angle_data = {**session_data, **chosen_angle}
        asset_type = session_data.get("asset_type")

        if asset_type == "Ad Copy": return await self.marketing_saga_stack.prophesy_ad_copy_from_angle(full_angle_data)
        elif asset_type in ["Landing Page", "Funnel Page"]: return await self.marketing_saga_stack.prophesy_page_html_from_angle(full_angle_data)
        elif asset_type in ["Affiliate Copy", "Email Copy"]: return await self.marketing_saga_stack.prophesy_affiliate_or_email_copy_from_angle(full_angle_data)
        else: raise ValueError(f"Unknown asset type '{asset_type}' requested.")

--- END OF FILE backend/engine.py ---