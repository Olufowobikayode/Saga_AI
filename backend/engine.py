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

# --- Import the STACKS ---
from backend.stacks.new_ventures_stack import NewVenturesStack
from backend.stacks.content_saga_stack import ContentSagaStack
from backend.stacks.grand_strategy_stack import GrandStrategyStack

logger = logging.getLogger(__name__)

class SagaEngine:
    """
    The SagaEngine is the heart of the application, the digital embodiment
    of the Norse goddess of wisdom...
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
            web_oracle=self.web_oracle,
            trend_scraper=self.trend_scraper,
            marketplace_oracle=self.marketplace_oracle
        )
        self.audit_analyzer = EcommerceAuditAnalyzer(self.gemini_api_key, self.marketplace_oracle)
        self.price_arbitrage_finder = PriceArbitrageFinder(self.gemini_api_key, self.marketplace_oracle)
        self.social_selling_strategist = SocialSellingStrategist(self.gemini_api_key, self.marketplace_oracle)
        self.product_route_suggester = ProductRouteSuggester(self.gemini_api_key, self.marketplace_oracle)
        
        # --- Cache for multi-stage prophecies and strategic sessions ---
        self.strategy_session_cache = {}

        logger.info("Saga is now fully conscious and ready to share her wisdom.")

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        # This method is complete and remains unchanged
        user_input_content_for_ai = None
        if user_content_text: user_input_content_for_ai = user_content_text
        elif user_content_url:
            scraped_content = await self.marketplace_oracle.read_user_store_scroll(user_content_url)
            if scraped_content: user_input_content_for_ai = scraped_content
        if user_input_content_for_ai:
            return f"**THE USER'S OWN SAGA (Their Writing Style):**\nAnalyze the tone, style, and vocabulary of the following text. When you weave your prophecy, you MUST adopt this voice so the wisdom feels as if it comes from within themselves.\n---\n{user_input_content_for_ai}\n---"
        return "You shall speak with the direct, wise, and prophetic voice of Saga."

    async def _resolve_country_context(self, user_ip_address: Optional[str], target_country_name: Optional[str]) -> Dict:
        # This method is complete and remains unchanged
        country_name, country_code, is_global = "Global", None, True
        if target_country_name and target_country_name.lower() != "global":
            try:
                country_entry = iso3166.countries.get(target_country_name)
                country_name, country_code, is_global = country_entry.name, country_entry.alpha2, False
            except KeyError:
                logger.warning(f"Realm '{target_country_name}' not in scrolls. Prophecy will be global.")
        # IP Geolocation logic would go here
        return {"country_name": country_name, "country_code": country_code, "is_global": is_global}

    # --- COMMANDER STACK METHOD (The new mandatory entry point) ---

    async def prophesy_grand_strategy(self, **kwargs) -> Dict:
        """
        Calls the Commander Stack to forge a master plan.
        Returns the prophecy and a `strategy_session_id` which acts as a key for all other stacks.
        """
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
        # Cache the entire output, which includes the prophecy and the retrieved histories
        self.strategy_session_cache[strategy_session_id] = strategy_data
        
        return {
            "strategy_session_id": strategy_session_id,
            "prophecy": strategy_data.get("prophecy")
        }

    # --- (All other methods remain as they were, awaiting their update in the next steps) ---
    async def prophesy_initial_ventures(self, **kwargs) -> Dict:
        return {"status": "Awaiting update to require strategy session"}

    async def prophesy_venture_blueprint(self, **kwargs) -> Dict:
        return {"status": "Awaiting update to require strategy session"}

    async def prophesy_content_sparks(self, **kwargs) -> Dict:
        return {"status": "Awaiting update to require strategy session"}

    async def prophesy_social_media_post(self, **kwargs) -> Dict:
        return {"status": "Awaiting update to require strategy session"}

    async def prophesy_insightful_comment(self, **kwargs) -> Dict:
        return {"status": "Awaiting update to require strategy session"}

    async def prophesy_blog_post_from_spark(self, **kwargs) -> Dict:
        return {"status": "Awaiting update to require strategy session"}

    async def prophesy_commerce_audit(self, **kwargs) -> Dict:
        return await self.audit_analyzer.run_audit_and_strategy(**kwargs)

    async def prophesy_arbitrage_paths(self, **kwargs) -> Dict:
        return await self.price_arbitrage_finder.divine_arbitrage_paths(**kwargs)
        
    async def prophesy_social_selling_saga(self, **kwargs) -> Dict:
        return await self.social_selling_strategist.devise_social_selling_saga(**kwargs)
        
    async def prophesy_product_route(self, **kwargs) -> Dict:
        kwargs['niche_interest'] = kwargs.get('interest')
        return await self.product_route_suggester.prophesy_product_route(**kwargs)
--- END OF FILE backend/engine.py ---