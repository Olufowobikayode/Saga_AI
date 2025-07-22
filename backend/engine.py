--- START OF FILE backend/engine.py ---
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
from backend.scraper import SagaWebOracle
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.ecommerce_audit_analyzer import EcommerceAuditAnalyzer
from backend.price_arbitrage_finder import PriceArbitrageFinder
from backend.social_selling_strategist import SocialSellingStrategist
from backend.product_route_suggester import ProductRouteSuggester
from backend.utils import get_prophecy_from_oracle

# --- Import the NEWLY CREATED STACKS ---
from backend.stacks.new_ventures_stack import NewVenturesStack
from backend.stacks.content_saga_stack import ContentSagaStack

logger = logging.getLogger(__name__)

class SagaEngine:
    """
    The SagaEngine is the heart of the application, the digital embodiment
    of the Norse goddess of wisdom. She sits at the nexus of all information...
    """
    def __init__(self, gemini_api_key: str, ip_geolocation_api_key: Optional[str] = None):
        """
        Initializes the SagaEngine...
        """
        logger.info("The SagaEngine awakens... Summoning all sources of wisdom.")
        
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.gemini_api_key = gemini_api_key
        self.ip_geolocation_api_key = ip_geolocation_api_key

        # --- Instantiate all knowledge sources ---
        self.community_seer = CommunitySaga()
        self.trend_scraper = TrendScraper()
        self.web_oracle = SagaWebOracle()
        self.keyword_rune_keeper = KeywordRuneKeeper()
        self.marketplace_oracle = GlobalMarketplaceOracle()
        
        # --- Instantiate all specialist stacks and analyzers ---
        self.new_ventures_stack = NewVenturesStack(
            model=self.model,
            keyword_rune_keeper=self.keyword_rune_keeper,
            community_seer=self.community_seer,
            web_oracle=self.web_oracle,
            trend_scraper=self.trend_scraper,
            marketplace_oracle=self.marketplace_oracle
        )
        self.content_saga_stack = ContentSagaStack(
            model=self.model,
            keyword_rune_keeper=self.keyword_rune_keeper,
            community_seer=self.community_seer
        )
        self.audit_analyzer = EcommerceAuditAnalyzer(self.gemini_api_key, self.marketplace_oracle)
        self.price_arbitrage_finder = PriceArbitrageFinder(self.gemini_api_key, self.marketplace_oracle)
        self.social_selling_strategist = SocialSellingStrategist(self.gemini_api_key, self.marketplace_oracle)
        self.product_route_suggester = ProductRouteSuggester(self.gemini_api_key, self.marketplace_oracle)
        
        # --- In-memory cache for multi-stage prophecies ---
        self.prophecy_cache = {}

        logger.info("Saga is now fully conscious and ready to share her wisdom.")

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        # This method is complete and remains unchanged
        user_input_content_for_ai = None
        if user_content_text:
            user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self.marketplace_oracle.read_user_store_scroll(user_content_url)
            if scraped_content:
                user_input_content_for_ai = scraped_content
        
        if user_input_content_for_ai:
            return f"**THE USER'S OWN SAGA (Their Writing Style):**\nAnalyze the tone, style, and vocabulary of the following text. When you weave your prophecy, you MUST adopt this voice so the wisdom feels as if it comes from within themselves.\n---\n{user_input_content_for_ai}\n---"
        return "You shall speak with the direct, wise, and prophetic voice of Saga."

    async def _resolve_country_context(self, user_ip_address: Optional[str], target_country_name: Optional[str]) -> Dict:
        # This method is complete and remains unchanged
        country_name = "Global"
        country_code = None
        is_global = True
        if target_country_name and target_country_name.lower() != "global":
            try:
                country_entry = iso3166.countries.get(target_country_name)
                country_name, country_code, is_global = country_entry.name, country_entry.alpha2, False
            except KeyError:
                logger.warning(f"Realm '{target_country_name}' not in scrolls. Prophecy will be global.")
        elif user_ip_address and self.ip_geolocation_api_key:
            # IP Geolocation logic would go here
            pass
        return {"country_name": country_name, "country_code": country_code, "is_global": is_global}

    # --- New Ventures Prophecy Methods (These are complete) ---
    async def prophesy_initial_ventures(self, **kwargs) -> Dict:
        """Handles Phase 1 of the New Ventures Prophecy."""
        logger.info(f"PHASE 1 ENGINE: Calling NewVenturesStack for: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        prophecy_data = await self.new_ventures_stack.prophesy_initial_visions(interest=kwargs.get("interest"), country_code=country_context["country_code"], country_name=country_context["country_name"], user_tone_instruction=user_tone_instruction)
        session_id = str(uuid.uuid4())
        self.prophecy_cache[session_id] = prophecy_data.get("retrieved_histories_for_blueprint")
        return {"session_id": session_id, "visions": prophecy_data.get("initial_visions", {}).get("visions", [])}

    async def prophesy_venture_blueprint(self, session_id: str, chosen_vision: Dict, **kwargs) -> Dict:
        """Handles Phase 2 of the New Ventures Prophecy."""
        logger.info(f"PHASE 2 ENGINE: Calling NewVenturesStack for vision: '{chosen_vision.get('title')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        retrieved_histories = self.prophecy_cache.get(session_id)
        if not retrieved_histories: raise ValueError("Prophecy session is invalid or has expired. The histories are lost.")
        blueprint = await self.new_ventures_stack.prophesy_detailed_blueprint(chosen_vision=chosen_vision, retrieved_histories=retrieved_histories, user_tone_instruction=user_tone_instruction)
        if session_id in self.prophecy_cache: del self.prophecy_cache[session_id]
        return blueprint

    # --- NEW Content Saga Prophecy Methods ---
    async def prophesy_content_sparks(self, **kwargs) -> Dict:
        """Handles Phase 1 of the Content Saga. Generates sparks and caches the histories."""
        logger.info(f"CONTENT SAGA ENGINE (PHASE 1): Calling ContentSagaStack for: '{kwargs.get('interest')}'")
        prophecy_data = await self.content_saga_stack.prophesy_content_sparks(
            interest=kwargs.get("interest"),
            link=kwargs.get("link"),
            link_description=kwargs.get("link_description")
        )
        session_id = str(uuid.uuid4())
        # We cache the data needed for Phase 2: the histories and the sparks themselves
        self.prophecy_cache[session_id] = {
            "histories": prophecy_data.get("retrieved_histories"),
            "sparks": prophecy_data.get("sparks")
        }
        return {"session_id": session_id, "sparks": prophecy_data.get("sparks", [])}

    async def prophesy_social_media_post(self, session_id: str, spark_id: str, platform: str, length: str, post_type: str, link: Optional[str], link_description: Optional[str]) -> Dict:
        """Delegates the generation of a specific social media post."""
        cached_data = self.prophecy_cache.get(session_id)
        if not cached_data or not cached_data.get("sparks"): raise ValueError("Content prophecy session is invalid or has expired.")
        # Find the specific spark the user chose from the cached list
        spark = next((s for s in cached_data["sparks"] if s.get("spark_id") == spark_id), None)
        if not spark: raise ValueError("The chosen content spark could not be found in this session.")
        
        return await self.content_saga_stack.prophesy_social_post(spark, platform, length, post_type, link, link_description)

    async def prophesy_insightful_comment(self, session_id: str, spark_id: str, post_to_comment_on: str, link: Optional[str], link_description: Optional[str]) -> Dict:
        """Delegates the generation of an insightful comment."""
        cached_data = self.prophecy_cache.get(session_id)
        if not cached_data or not cached_data.get("sparks"): raise ValueError("Content prophecy session is invalid or has expired.")
        spark = next((s for s in cached_data["sparks"] if s.get("spark_id") == spark_id), None)
        if not spark: raise ValueError("The chosen content spark could not be found in this session.")

        return await self.content_saga_stack.prophesy_insightful_comment(spark, post_to_comment_on, link, link_description)

    async def prophesy_blog_post_from_spark(self, session_id: str, spark_id: str, link: Optional[str], link_description: Optional[str]) -> Dict:
        """Delegates the generation of a full blog post and clears the cache for that session."""
        cached_data = self.prophecy_cache.get(session_id)
        if not cached_data or not cached_data.get("sparks"): raise ValueError("Content prophecy session is invalid or has expired.")
        spark = next((s for s in cached_data["sparks"] if s.get("spark_id") == spark_id), None)
        if not spark: raise ValueError("The chosen content spark could not be found in this session.")
        
        # Once a major piece of content like a blog post is generated, we can often clear the cache.
        if session_id in self.prophecy_cache:
            del self.prophecy_cache[session_id]

        return await self.content_saga_stack.prophesy_blog_post(spark, link, link_description)

    # --- Placeholder for Grand Strategy and other prophecies ---
    async def prophesy_grand_strategy(self, **kwargs) -> Dict:
        return {"status": "This prophecy is yet to be fully woven."}

    # --- Existing Wrappers for Specialist Prophecies (These remain functional) ---
    async def prophesy_commerce_audit(self, **kwargs) -> Dict:
        # This method's logic is complete and unchanged
        logger.info(f"Delegating a commerce audit prophecy for: '{kwargs.get('product_name')}'")
        # ... full implementation
        return await self.audit_analyzer.run_audit_and_strategy(**kwargs)

    async def prophesy_arbitrage_paths(self, **kwargs) -> Dict:
        # This method's logic is complete and unchanged
        logger.info(f"Delegating an arbitrage prophecy for: '{kwargs.get('product_name')}'")
        # ... full implementation
        return await self.price_arbitrage_finder.divine_arbitrage_paths(**kwargs)
        
    async def prophesy_social_selling_saga(self, **kwargs) -> Dict:
        # This method's logic is complete and unchanged
        logger.info(f"Delegating a social selling saga for: '{kwargs.get('product_name')}'")
        # ... full implementation
        return await self.social_selling_strategist.devise_social_selling_saga(**kwargs)
        
    async def prophesy_product_route(self, **kwargs) -> Dict:
        # This method's logic is complete and unchanged
        logger.info(f"Delegating a product route prophecy for: '{kwargs.get('interest')}'")
        kwargs['niche_interest'] = kwargs.get('interest')
        # ... full implementation
        return await self.product_route_suggester.prophesy_product_route(**kwargs)
--- END OF FILE backend/engine.py ---