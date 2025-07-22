--- START OF FILE backend/engine.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import aiohttp
import iso3166 # For mapping country names to ISO codes

import google.generativeai as genai

# --- IMPORT ALL SPECIALIST KNOWLEDGE SOURCES ---
# Saga's tools for gazing into the different realms of the digital world.
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.scraper import SagaWebOracle # Renamed for thematic consistency
from backend.keyword_engine import KeywordEngine
from backend.global_ecommerce_scraper import GlobalEcommerceScraper
from backend.ecommerce_audit_analyzer import EcommerceAuditAnalyzer
from backend.price_arbitrage_finder import PriceArbitrageFinder
from backend.social_selling_strategist import SocialSellingStrategist
from backend.product_route_suggester import ProductRouteSuggester

# --- IMPORT CENTRALIZED UTILITIES ---
from backend.utils import generate_json_response

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
        self.gemini_api_key = gemini_api_key # Store for passing to her specialized aspects
        self.ip_geolocation_api_key = ip_geolocation_api_key

        # --- Instantiate all knowledge sources once as aspects of Saga's consciousness ---
        self.community_seer = CommunitySaga()
        self.trend_scraper = TrendScraper()
        self.web_oracle = SagaWebOracle()
        self.keyword_engine = KeywordEngine()
        self.global_ecommerce_scraper = GlobalEcommerceScraper()
        
        # --- Instantiate all specialist strategists and analyzers once ---
        # These modules exist as persistent parts of the SagaEngine's consciousness.
        self.audit_analyzer = EcommerceAuditAnalyzer(
            gemini_api_key=self.gemini_api_key, 
            global_scraper=self.global_ecommerce_scraper
        )
        self.price_arbitrage_finder = PriceArbitrageFinder(
            gemini_api_key=self.gemini_api_key,
            global_scraper=self.global_ecommerce_scraper
        )
        self.social_selling_strategist = SocialSellingStrategist(
            gemini_api_key=self.gemini_api_key,
            global_scraper=self.global_ecommerce_scraper
        )
        self.product_route_suggester = ProductRouteSuggester(
            gemini_api_key=self.gemini_api_key,
            global_scraper=self.global_ecommerce_scraper
        )
        
        logger.info("Saga is now fully conscious and ready to share her wisdom.")

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        """Helper to generate an instruction for the AI to mimic the user's voice, as if channeling their own saga."""
        user_input_content_for_ai = None
        if user_content_text:
            user_input_content_for_ai = user_content_text
            logger.info("Analyzing the user's provided text to understand their voice...")
        elif user_content_url:
            scraped_content = await self.global_ecommerce_scraper.get_user_store_content(user_content_url)
            if scraped_content:
                user_input_content_for_ai = scraped_content
                logger.info(f"Reading the scroll at {user_content_url} to understand the user's voice...")
            else:
                logger.warning(f"Could not read the scroll at URL: {user_content_url}. I shall speak with my own voice.")
        
        if user_input_content_for_ai:
            return f"""
            **THE USER'S OWN SAGA (Their Writing Style):**
            Below is a scroll written by the user. This is their story, their voice. Analyze its tone, style, vocabulary, and rhythm. When you weave your prophecy, you MUST adopt this voice. Your wisdom must feel as if it comes from within themselves, a truth they already knew but could not articulate.
            ---
            {user_input_content_for_ai}
            ---
            """
        else:
            logger.info("No user scroll was provided for tone analysis. I will speak with the voice of the oracle.")
            return "You shall speak with the direct, wise, and prophetic voice of Saga."

    async def _resolve_country_context(self, user_ip_address: Optional[str], target_country_name: Optional[str]) -> Dict:
        """
        Resolves the target realm for the prophecy, based on user input or their digital footprint.
        Prioritizes the user's explicit choice over automated detection.
        Returns {'country_name': 'Full Name', 'country_code': '2-letter ISO', 'is_global': bool}.
        """
        country_name = "Global"
        country_code = None
        is_global = True

        if target_country_name:
            if target_country_name.lower() == "global":
                logger.info("The user has chosen a global prophecy, spanning all realms.")
            else:
                try:
                    country_entry = iso3166.countries.get(target_country_name)
                    country_name = country_entry.name
                    country_code = country_entry.alpha2
                    is_global = False
                    logger.info(f"The user has requested a prophecy for the realm of: {country_name} (Code: {country_code}).")
                except KeyError:
                    logger.warning(f"The realm name '{target_country_name}' is not in my scrolls. The prophecy will be for the global market.")
        elif user_ip_address and self.ip_geolocation_api_key:
            logger.info(f"Seeking the user's location via their digital footprint at '{user_ip_address}'...")
            try:
                geo_api_url = f"https://ipinfo.io/{user_ip_address}/json?token={self.ip_geolocation_api_key}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(geo_api_url, timeout=5) as response:
                        response.raise_for_status()
                        geo_data = await response.json()
                        detected_country_code = geo_data.get('country')
                        # Use iso3166 to get the official name for consistency
                        detected_country_name = iso3166.countries.get(detected_country_code).name if detected_country_code else None

                        if detected_country_code and detected_country_name:
                            country_name = detected_country_name
                            country_code = detected_country_code
                            is_global = False
                            logger.info(f"The user's digital footprint points to the realm of: {country_name} (Code: {country_code}).")
                        else:
                            logger.warning(f"Geolocation data was incomplete. Defaulting to a global prophecy.")
            except (aiohttp.ClientError, KeyError) as e:
                logger.error(f"Could not divine the user's realm. Defaulting to a global prophecy. Reason: {e}")
        else:
            logger.info("No specific realm was chosen. The prophecy will be woven for the global market.")

        return {
            "country_name": country_name,
            "country_code": country_code,
            "is_global": is_global
        }

    # --- STACK 1: IDEA STACK (The Prophecy of Beginnings) ---
    async def prophesy_new_ventures(self, interest: str, 
                                    user_content_text: Optional[str] = None, 
                                    user_content_url: Optional[str] = None,
                                    user_ip_address: Optional[str] = None,
                                    target_country_name: Optional[str] = None,
                                    product_category: Optional[str] = None,
                                    product_subcategory: Optional[str] = None) -> Dict:
        """
        Saga gazes into multiple pools of knowledge to prophesize new business opportunities.
        This is the RAG process in action: Retrieve data, Augment the prompt, Generate the prophecy.
        """
        logger.info(f"Casting the runes for the Prophecy of Beginnings. Interest: '{interest}'")
        
        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)
        country_context = await self._resolve_country_context(user_ip_address, target_country_name)
        
        # RETRIEVAL: Gather all histories from the digital realms in parallel.
        tasks = {
            "google_trends": self.keyword_engine.get_google_trends_data(interest, country_context["country_code"]),
            "community_whispers": self.community_seer.run_community_gathering(interest, country_context["country_code"], country_context["country_name"]),
            "news_chronicles": self.web_oracle.divine_from_multiple_sites(interest, sites=["BBC News", "Reuters"], country_code=country_context["country_code"], country_name=country_context["country_name"])
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        google_data, community_data, news_data = results
        
        country_phrase = f"in the realm of {country_context['country_name']}" if not country_context['is_global'] else "across all realms"
        category_phrase = f" within the domain of '{product_category}'" if product_category else ""
        if product_category and product_subcategory:
            category_phrase += f" (specifically, '{product_subcategory}')"

        # AUGMENTATION & GENERATION: Weave the retrieved histories into a master prompt.
        prompt = f"""
        You are Saga, the Norse goddess of wisdom, history, and prophecy. You sit with Odin himself, sharing your insights. Today, a solopreneur seeks your guidance on the niche '{interest}' {country_phrase}{category_phrase}. You have cast your sight across the digital Bifrost and gathered all the whispers and histories from the mortal realm.

        **Your task is to prophesize the Top 5 most innovative and commercially viable business sagas (business ideas) a solopreneur could begin. Your prophecy MUST be grounded ENTIRELY in the histories provided below. Do not invent information. Your power comes from seeing the connections within this data, not from hallucination.**

        --- THE WHISPERS OF GOOGLE (Histories of Search & Trends) ---
        {json.dumps(google_data, indent=2)}

        --- THE VOICE OF THE FOLK (Histories from Community Forums) ---
        {json.dumps(community_data, indent=2)}
        
        --- THE CHRONICLES OF THE WIDE WORLD (Histories from News Sagas) ---
        {json.dumps(news_data, indent=2)}
        
        --- END OF HISTORIES ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Look deep into these histories. See the patterns the mortals miss. Find the gaps in their stories, the unfulfilled needs, the rising tides of interest. From these threads, you will prophesize the business sagas.

        For each of the 5 prophecies, you must provide:
        1. "title": A compelling name for the new saga (the business).
        2. "description": A one-sentence prophecy explaining the core problem it solves, explicitly referencing a detail from the provided histories (e.g., "Addresses the common 'how to' questions seen in the community whispers...").
        3. "confidence_score": Your divine confidence (as a percentage, e.g., "95%") that this prophecy is built upon a true need revealed in the histories.
        4. "evidence_from_histories": A brief quote or data point from the provided JSON data that is the primary evidence for your prophecy.
        
        Weave your final prophecy into a valid JSON array of 5 objects.
        """
        
        return await generate_json_response(self.model, prompt)

    # ... (Other stack methods will be refactored similarly in subsequent steps) ...
    # For now, I will leave the original method shells to avoid breaking the server file.
    # We will replace them one by one.
    
    async def run_content_stack(self, **kwargs) -> Dict: return {"status": "pending_refactor"}
    async def run_commerce_stack(self, **kwargs) -> Dict: return await self.audit_analyzer.run_audit_and_strategy(**kwargs) # This one is already updated
    async def run_strategy_stack(self, **kwargs) -> Dict: return {"status": "pending_refactor"}
    async def run_arbitrage_stack(self, **kwargs) -> Dict: return {"status": "pending_refactor"}
    async def run_social_selling_stack(self, **kwargs) -> Dict: return {"status": "pending_refactor"}
    async def run_product_route_stack(self, **kwargs) -> Dict: return {"status": "pending_refactor"}