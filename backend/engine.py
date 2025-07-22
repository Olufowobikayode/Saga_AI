--- START OF FILE backend/engine.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import aiohttp
import iso3166
import uuid

import google.generativeai as genai

# --- IMPORT ALL SPECIALIST KNOWLEDGE SOURCES ---
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

# --- Import the NEWLY CREATED STACK ---
from backend.stacks.new_ventures_stack import NewVenturesStack

logger = logging.getLogger(__name__)

class SagaEngine:
    """
    The SagaEngine is the heart of the application, the digital embodiment
    of the Norse goddess of wisdom. She sits at the nexus of all information,
    orchestrating her specialized aspects—her seers and oracles—to weave raw data
    into coherent sagas, offering prophetic insights and wise counsel to solopreneurs.
    """
    def __init__(self, gemini_api_key: str, ip_geolocation_api_key: Optional[str] = None):
        """
        Initializes the SagaEngine. Upon creation, she awakens her sources of wisdom—
        the specialist scrapers, oracles, and analyzers—and configures her connection
        to the cosmic AI oracle (Gemini). This is done once for maximum efficiency.
        """
        logger.info("The SagaEngine awakens... Summoning all sources of wisdom.")
        
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.gemini_api_key = gemini_api_key
        self.ip_geolocation_api_key = ip_geolocation_api_key

        # --- Instantiate all knowledge sources once as aspects of Saga's consciousness ---
        self.community_seer = CommunitySaga()
        self.trend_scraper = TrendScraper()
        self.web_oracle = SagaWebOracle()
        self.keyword_rune_keeper = KeywordRuneKeeper()
        self.marketplace_oracle = GlobalMarketplaceOracle()
        
        # --- Instantiate all specialist strategists AND THE NEW STACK ---
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
        
        # --- Simple in-memory cache for multi-stage prophecies ---
        self.prophecy_cache = {}

        logger.info("Saga is now fully conscious and ready to share her wisdom.")

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        """Helper to generate an instruction for the AI to mimic the user's voice, as if channeling their own saga."""
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
        """Resolves the target realm for the prophecy."""
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
            logger.info(f"Seeking the user's location via their digital footprint at '{user_ip_address}'...")
            try:
                geo_api_url = f"https://ipinfo.io/{user_ip_address}/json?token={self.ip_geolocation_api_key}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(geo_api_url, timeout=5) as response:
                        response.raise_for_status()
                        geo_data = await response.json()
                        detected_country_code = geo_data.get('country')
                        detected_country_name = iso3166.countries.get(detected_country_code).name if detected_country_code else None
                        if detected_country_code and detected_country_name:
                            country_name, country_code, is_global = detected_country_name, detected_country_code, False
            except (aiohttp.ClientError, KeyError, Exception) as e:
                logger.error(f"Could not divine the user's realm. Defaulting to a global prophecy. Reason: {e}")
        return {"country_name": country_name, "country_code": country_code, "is_global": is_global}

    # --- NEW TWO-PHASE PROPHECY METHODS ---

    async def prophesy_initial_ventures(self, **kwargs) -> Dict:
        """
        Handles Phase 1 of the New Ventures Prophecy.
        Generates 10 initial visions and caches the data for Phase 2.
        """
        logger.info(f"PHASE 1 ENGINE: Calling NewVenturesStack for: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))

        prophecy_data = await self.new_ventures_stack.prophesy_initial_visions(
            interest=kwargs.get("interest"),
            country_code=country_context["country_code"],
            country_name=country_context["country_name"],
            user_tone_instruction=user_tone_instruction
        )
        
        session_id = str(uuid.uuid4())
        self.prophecy_cache[session_id] = prophecy_data.get("retrieved_histories_for_blueprint")
        
        return {
            "session_id": session_id,
            "visions": prophecy_data.get("initial_visions", {}).get("visions", [])
        }

    async def prophesy_venture_blueprint(self, session_id: str, chosen_vision: Dict, **kwargs) -> Dict:
        """
        Handles Phase 2 of the New Ventures Prophecy.
        Generates a detailed blueprint for a chosen vision using cached data.
        """
        logger.info(f"PHASE 2 ENGINE: Calling NewVenturesStack for vision: '{chosen_vision.get('title')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))

        retrieved_histories = self.prophecy_cache.get(session_id)
        if not retrieved_histories:
            raise ValueError("Prophecy session is invalid or has expired. The histories are lost.")
            
        blueprint = await self.new_ventures_stack.prophesy_detailed_blueprint(
            chosen_vision=chosen_vision,
            retrieved_histories=retrieved_histories,
            user_tone_instruction=user_tone_instruction
        )
        
        if session_id in self.prophecy_cache:
            del self.prophecy_cache[session_id]
        
        return blueprint

    # --- OTHER SINGLE-PHASE PROPHECY METHODS ---

    async def prophesy_content_saga(self, **kwargs) -> Dict:
        # This would be the next candidate for conversion to its own stack file.
        logger.info(f"Weaving a Content Saga for interest: '{kwargs.get('interest')}'")
        # ... implementation ...
        return {"status": "placeholder"}
    
    # ... other methods like prophesy_grand_strategy etc. ...

    # --- WRAPPERS FOR SPECIALIST PROPHECIES ---

    async def prophesy_commerce_audit(self, **kwargs) -> Dict:
        """Delegates the deep divination of a single product to the Audit Analyzer aspect."""
        logger.info(f"Delegating a commerce audit prophecy for: '{kwargs.get('product_name')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        
        # This is messy; the analyzer should ideally take the context itself.
        # For now, we manually add keys, but this can be cleaned up later.
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            "target_country_code": country_context["country_code"],
            "country_name_for_ai": country_context["country_name"],
            "is_global_search": country_context["is_global"]
        })
        return await self.audit_analyzer.run_audit_and_strategy(**kwargs)

    async def prophesy_arbitrage_paths(self, **kwargs) -> Dict:
        """Delegates the search for hidden value to the Price Arbitrage Finder aspect."""
        logger.info(f"Delegating an arbitrage prophecy for: '{kwargs.get('product_name')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            "target_country_code": country_context["country_code"],
            "country_name_for_ai": country_context["country_name"]
        })
        return await self.price_arbitrage_finder.divine_arbitrage_paths(**kwargs)

    async def prophesy_social_selling_saga(self, **kwargs) -> Dict:
        """Delegates the weaving of a social selling saga to the Weaver of Influence aspect."""
        logger.info(f"Delegating a social selling saga for: '{kwargs.get('product_name')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            "target_country_name": country_context["country_name"]
        })
        return await self.social_selling_strategist.devise_social_selling_saga(**kwargs)
        
    async def prophesy_product_route(self, **kwargs) -> Dict:
        """Delegates the finding of a clear path to the Pathfinder aspect."""
        logger.info(f"Delegating a product route prophecy for: '{kwargs.get('niche_interest')}'")
        # The key in kwargs is 'interest', but the method expects 'niche_interest'
        kwargs['niche_interest'] = kwargs.get('interest')
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            "target_country_name": country_context["country_name"]
        })
        return await self.product_route_suggester.prophesy_product_route(**kwargs)
--- END OF FILE backend/engine.py ---