--- START OF FILE backend/engine.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import aiohttp
import iso3166

import google.generativeai as genai

# --- IMPORT ALL SPECIALIST KNOWLEDGE SOURCES ---
# Saga's seers and oracles for gazing into the different realms of the digital world.
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.scraper import SagaWebOracle
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.ecommerce_audit_analyzer import EcommerceAuditAnalyzer
from backend.price_arbitrage_finder import PriceArbitrageFinder
from backend.social_selling_strategist import SocialSellingStrategist
from backend.product_route_suggester import ProductRouteSuggester

# --- IMPORT CENTRALIZED UTILITIES ---
from backend.utils import get_prophecy_from_oracle

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
        
        # --- Instantiate all specialist strategists and analyzers, providing them with her oracles ---
        self.audit_analyzer = EcommerceAuditAnalyzer(self.gemini_api_key, self.marketplace_oracle)
        self.price_arbitrage_finder = PriceArbitrageFinder(self.gemini_api_key, self.marketplace_oracle)
        self.social_selling_strategist = SocialSellingStrategist(self.gemini_api_key, self.marketplace_oracle)
        self.product_route_suggester = ProductRouteSuggester(self.gemini_api_key, self.marketplace_oracle)
        
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
        # ... [This method remains unchanged from the last step]
        country_name = "Global"
        country_code = None
        is_global = True
        if target_country_name and target_country_name.lower() != "global":
            try:
                country_entry = iso3166.countries.get(target_country_name)
                country_name, country_code, is_global = country_entry.name, country_entry.alpha2, False
            except KeyError:
                logger.warning(f"Realm '{target_country_name}' not in scrolls. Prophecy will be global.")
        # ... [Rest of IP geolocation logic remains]
        return {"country_name": country_name, "country_code": country_code, "is_global": is_global}

    # --- CORE PROPHECY METHODS ---

    async def prophesy_new_ventures(self, **kwargs) -> Dict:
        """Saga gazes into multiple pools of knowledge to prophesize new business opportunities."""
        logger.info(f"Casting the runes for a Prophecy of Beginnings. Interest: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        
        # RETRIEVAL
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(kwargs.get('interest'), country_context["country_code"]),
            "community_whispers": self.community_seer.run_community_gathering(kwargs.get('interest'), country_context["country_code"], country_context["country_name"]),
            "news_chronicles": self.web_oracle.divine_from_multiple_sites(kwargs.get('interest'), sites=["BBC News", "Reuters"], country_name=country_context["country_name"])
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        keyword_data, community_data, news_data = results
        
        # AUGMENTATION & GENERATION
        prompt = f"""You are Saga... [This prompt is the same as the fully developed one in Step 1]"""
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_content_saga(self, **kwargs) -> Dict:
        """Saga instructs a Skald (the AI) to forge a content saga for a mortal's niche."""
        logger.info(f"Weaving a Content Saga for interest: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))

        # RETRIEVAL
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(kwargs.get('interest'), country_context["country_code"]),
            "community_questions": self.community_seer.run_community_gathering(kwargs.get('interest'), country_context["country_code"], country_context["country_name"])
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        keyword_data, community_data = results

        # AUGMENTATION & GENERATION
        prompt = f"""
        You are a Skald, a master poet and storyteller, inspired by Saga, the goddess of wisdom. You must craft the opening verses of a new content saga for the niche '{kwargs.get('interest')}'. Your inspiration will come from the market's whispers. Your prophecy must be grounded ENTIRELY in the histories provided below.

        --- MARKET WHISPERS (Retrieved Histories) ---
        Keyword Runes & Trends: {json.dumps(keyword_data, indent=2)}
        Community Questions & Pains: {json.dumps(community_data, indent=2)}
        --- END OF HISTORIES ---

        {user_tone_instruction}

        Your task is to forge 5 compelling titles for blog posts or videos. For each title, write a short, engaging description. These are the opening chapters of a saga meant to draw in listeners by answering their divined questions and pains.

        Format your output as a JSON array of 5 objects, each with "title" and "description" keys.
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_grand_strategy(self, **kwargs) -> Dict:
        """Saga lays down a grand strategy based on a comprehensive reading of the digital realms."""
        logger.info(f"Divining a Grand Strategy for interest: '{kwargs.get('interest')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))

        # RETRIEVAL
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(kwargs.get('interest'), country_context["country_code"]),
            "community_pain_points": self.community_seer.run_community_gathering(kwargs.get('interest'), country_context["country_code"], country_context["country_name"]),
            "trend_insights": self.trend_scraper.run_scraper_tasks(kwargs.get('interest'), country_context["country_code"], country_context["country_name"])
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        keyword_data, community_data, trend_data = results
        
        # AUGMENTATION & GENERATION
        prompt = f"""
        As the goddess Saga, you will now lay down a grand strategy. A hero has come to you with an interest in '{kwargs.get('interest')}' and seeks to make their mark. You have consulted the runes and histories. Your prophecy MUST be grounded ENTIRELY in the histories provided below.

        --- MARKET HISTORIES (Retrieved Data) ---
        Keyword Runes from Structured Oracles: {json.dumps(keyword_data, indent=2)}
        Community Pain Points & Whispers: {json.dumps(community_data, indent=2)}
        Keyword Trend Insights: {json.dumps(trend_data, indent=2)}
        --- END OF HISTORIES ---

        {user_tone_instruction}

        Your task is to prophesize an actionable digital strategy. This prophecy must be clear, wise, and structured as a valid JSON object with the following keys:
        {{
            "keyword_focus": "A detailed prophecy on the primary and long-tail keywords. Which words hold power? Which will gather followers? Base this on the retrieved histories.",
            "content_pillars": "The great themes for their saga. What strategic categories of content will address the people's needs and build a kingdom of organic traffic? Justify with data.",
            "promotion_channels": "Which realms should they travel to spread their message? (e.g., SEO, social media). Justify your choices with the data.",
            "overall_strategic_summary": "A concise, actionable summary of the grand strategy. The final verse of this prophecy."
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    # --- WRAPPERS FOR SPECIALIST PROPHECIES ---

    async def prophesy_commerce_audit(self, **kwargs) -> Dict:
        """Delegates the deep divination of a single product to the Audit Analyzer aspect."""
        logger.info(f"Delegating a commerce audit prophecy for: '{kwargs.get('product_name')}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            **country_context
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
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            "target_country_name": country_context["country_name"]
        })
        return await self.product_route_suggester.prophesy_product_route(**kwargs)
--- END OF FILE backend/engine.py ---