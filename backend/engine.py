--- START OF FILE backend/engine.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import aiohttp
import iso3166 # For mapping country names to ISO codes

import google.generativeai as genai

# --- IMPORT ALL SPECIALIST KNOWLEDGE SOURCES ---
from backend.q_and_a import UniversalScraper
from backend.trends import TrendScraper
from backend.scraper import WebScraper
from backend.keyword_engine import KeywordEngine as GoogleApiEngine
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
    The SagaEngine is the heart of the Saga AI application, the digital embodiment
    of the Norse goddess of wisdom. It orchestrates all specialized knowledge sources
    to weave raw data into a coherent saga, offering prophetic insights and wise 
    counsel to solopreneurs.
    """
    def __init__(self, gemini_api_key: str, ip_geolocation_api_key: Optional[str] = None):
        """
        Initializes the SagaEngine. Upon creation, it gathers all its sources of wisdom—
        the specialist scrapers and analyzers—and configures the AI oracle (Gemini).
        This is done once for maximum efficiency.
        """
        logger.info("The SagaEngine awakens... Initializing all sources of wisdom.")
        
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.gemini_api_key = gemini_api_key # Store for passing to sub-modules
        self.ip_geolocation_api_key = ip_geolocation_api_key

        # --- Instantiate all knowledge sources once ---
        self.q_and_a_scraper = UniversalScraper()
        self.trend_tool_scraper = TrendScraper()
        self.general_scraper = WebScraper()
        self.google_engine = GoogleApiEngine()
        self.global_ecommerce_scraper = GlobalEcommerceScraper()
        
        # --- Instantiate all specialist strategists and analyzers once ---
        # This resolves the "redundant instantiation" weakness. These modules now exist
        # as persistent parts of the SagaEngine's consciousness.
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
        
        logger.info("SagaEngine is now fully conscious and ready to share its wisdom.")

    # _generate_json_response has been removed and is now imported from utils.py

    async def _get_user_tone_instruction(self, user_content_text: Optional[str], user_content_url: Optional[str]) -> str:
        """Helper to generate AI instruction for mimicking user tone by fetching and processing user content."""
        user_input_content_for_ai = None
        if user_content_text:
            user_input_content_for_ai = user_content_text
            logger.info("Analyzing provided text to understand the user's voice.")
        elif user_content_url:
            scraped_content = await self.global_ecommerce_scraper.get_user_store_content(user_content_url)
            if scraped_content:
                user_input_content_for_ai = scraped_content
                logger.info(f"Analyzing content from {user_content_url} to understand the user's voice.")
            else:
                logger.warning(f"Could not read content from URL: {user_content_url}. Proceeding with default voice.")
        
        if user_input_content_for_ai:
            return f"""
            **USER'S WRITING STYLE REFERENCE (THEIR SAGA):**
            Below is content provided by the user. This is their story, their voice. Analyze its tone, style, vocabulary, and rhythm. When you generate your prophecy, you MUST adopt this voice. Speak as they would speak, so the wisdom feels as if it comes from within themselves.
            ---
            {user_input_content_for_ai}
            ---
            """
        else:
            logger.info("No user content provided for tone analysis. Using the default voice of the oracle.")
            return "You will speak with a direct, professional, and encouraging voice."

    async def _resolve_country_context(self, user_ip_address: Optional[str], target_country_name: Optional[str]) -> Dict:
        """
        Resolves the target realm for the prophecy, based on user input or IP address.
        Prioritizes explicit selection over IP detection.
        Returns {'country_name': 'Full Name', 'country_code': '2-letter ISO', 'is_global': bool}.
        """
        country_name = "Global"
        country_code = None
        is_global = True

        if target_country_name:
            if target_country_name.lower() == "global":
                logger.info("User has chosen a global prophecy.")
            else:
                try:
                    country_entry = iso3166.countries.get(target_country_name)
                    if country_entry:
                        country_name = country_entry.name
                        country_code = country_entry.alpha2
                        is_global = False
                        logger.info(f"User has requested a prophecy for the realm of: {country_name} (Code: {country_code}).")
                    else:
                        logger.warning(f"Could not recognize the realm name '{target_country_name}'. The prophecy will be for the global market.")
                except KeyError:
                    logger.warning(f"Invalid realm name '{target_country_name}' provided. The prophecy will be for the global market.")
        elif user_ip_address and self.ip_geolocation_api_key:
            logger.info(f"Seeking user's location via their digital footprint at '{user_ip_address}'...")
            try:
                geo_api_url = f"https://ipinfo.io/{user_ip_address}/json?token={self.ip_geolocation_api_key}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(geo_api_url, timeout=5) as response:
                        response.raise_for_status()
                        geo_data = await response.json()
                        detected_country_code = geo_data.get('country')
                        detected_country_name = geo_data.get('country_name')

                        if detected_country_code and detected_country_name:
                            country_name = detected_country_name
                            country_code = detected_country_code
                            is_global = False
                            logger.info(f"Digital footprint points to the realm of: {country_name} (Code: {country_code}).")
                        else:
                            logger.warning(f"Geolocation data incomplete for IP '{user_ip_address}'. Defaulting to a global prophecy.")
            except aiohttp.ClientError as e:
                logger.error(f"Geolocation API call failed for IP '{user_ip_address}': {e}. Defaulting to a global prophecy.")
            except Exception as e:
                logger.error(f"Unexpected error during geolocation for IP '{user_ip_address}': {e}. Defaulting to a global prophecy.")
        else:
            logger.info("No specific realm selected and no digital footprint provided/resolved. The prophecy will be for the global market.")

        return {
            "country_name": country_name,
            "country_code": country_code,
            "is_global": is_global
        }

    # --- STACK 1: IDEA STACK LOGIC ---
    async def run_idea_stack(self, interest: str, 
                             user_content_text: Optional[str] = None, 
                             user_content_url: Optional[str] = None,
                             user_ip_address: Optional[str] = None,
                             target_country_name: Optional[str] = None,
                             product_category: Optional[str] = None,
                             product_subcategory: Optional[str] = None) -> Dict:
        """
        Orchestrates the full data pipeline for the Idea Stack. It gazes into
        multiple pools of knowledge to prophesize new opportunities.
        """
        logger.info(f"Casting the runes for the Idea Stack. Interest: '{interest}'")
        
        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)
        country_context = await self._resolve_country_context(user_ip_address, target_country_name)
        
        tasks = {
            "google_trends": self.google_engine.get_full_keyword_strategy_data(
                interest, country_context["country_code"], country_context["country_name"],
                product_category, product_subcategory
            ),
            "community_insights": self.q_and_a_scraper.run_scraping_tasks(
                interest, country_context["country_code"], country_context["country_name"]
            ),
            "keyword_tool_trends": self.trend_tool_scraper.run_scraper_tasks(
                interest, country_context["country_code"], country_context["country_name"],
                product_category, product_subcategory
            ),
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Unpack results with error handling
        google_data = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        community_data = results[1] if not isinstance(results[1], Exception) else [{"error": str(results[1])}]
        keyword_tool_data = results[2] if not isinstance(results[2], Exception) else [{"error": str(results[2])}]

        country_phrase = f"in {country_context['country_name']}" if not country_context['is_global'] else "globally"
        category_phrase = f" in the '{product_category}' category" if product_category else ""
        if product_category and product_subcategory:
            category_phrase += f" (subcategory: '{product_subcategory}')"

        prompt = f"""
        You are Saga, the Norse goddess of wisdom, history, and prophecy. You sit with Odin himself, sharing your insights. Today, a solopreneur seeks your guidance on the niche '{interest}' {country_phrase}{category_phrase}. You have gathered all the whispers and histories from the mortal realm:

        --- PILLAR 1: THE WHISPERS OF GOOGLE (Trends & Search) ---
        {json.dumps(google_data, indent=2)}

        --- PILLAR 2: THE VOICE OF THE FOLK (Community & Q&A) ---
        {json.dumps(community_data, indent=2)}
        
        --- PILLAR 3: THE CHANTS OF THE SEEKERS (Keyword Tools) ---
        {json.dumps(keyword_tool_data, indent=2)}
        --- END OF HISTORIES ---

        {user_tone_instruction}

        **Your Prophetic Task:**
        Look deep into this data. See the patterns the mortals miss. Find the gaps in their stories, the unfulfilled needs. From this, you will prophesize the **Top 5 most innovative and commercially viable business sagas** a solopreneur could begin.

        For each prophecy, provide:
        1. "title": A compelling name for the new saga (the business).
        2. "description": A one-sentence prophecy explaining the core problem it solves, referencing the histories you have gathered.
        3. "confidence_score": Your divine confidence (as a percentage, e.g., "95%") that this prophecy is built on a true need in the market.
        
        Weave your final prophecy into a valid JSON array of objects.
        """
        
        return await generate_json_response(self.model, prompt)

    # --- STACK 2: CONTENT STACK LOGIC ---
    async def run_content_stack(self, interest: str, 
                                  user_content_text: Optional[str] = None, 
                                  user_content_url: Optional[str] = None,
                                  user_ip_address: Optional[str] = None,
                                  target_country_name: Optional[str] = None,
                                  product_category: Optional[str] = None,
                                  product_subcategory: Optional[str] = None) -> Dict:
        logger.info(f"Weaving a Content Saga for interest: '{interest}'")
        
        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)
        country_context = await self._resolve_country_context(user_ip_address, target_country_name)

        tasks = {
            "google_trends_keywords": self.google_engine.get_full_keyword_strategy_data(
                interest, country_context["country_code"], country_context["country_name"],
                product_category, product_subcategory
            ),
            "community_questions": self.q_and_a_scraper.run_scraping_tasks(
                interest, country_context["country_code"], country_context["country_name"]
            )
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        google_keywords = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        community_questions = results[1] if not isinstance(results[1], Exception) else [{"error": str(results[1])}]

        country_phrase = f"for the {country_context['country_name']} market" if not country_context['is_global'] else "globally"
        category_phrase = f" in the '{product_category}' category" if product_category else ""
        if product_category and product_subcategory:
            category_phrase += f" (subcategory: '{product_subcategory}')"

        prompt = f"""
        You are a Skald, a master poet and storyteller, inspired by Saga, the goddess of wisdom. You must craft the opening verses of a new content saga for the niche '{interest}' {country_phrase}{category_phrase}. Your inspiration will come from the whispers of the market:

        --- MARKET WHISPERS ---
        Google Trends & Keywords: {json.dumps(google_keywords, indent=2)}
        Community Questions & Pains: {json.dumps(community_questions, indent=2)}
        --- END OF WHISPERS ---

        {user_tone_instruction}

        Your task is to forge 5 compelling titles for blog posts or videos. For each title, write a short, engaging description. These are the opening chapters of a saga meant to draw in listeners, solve their problems, and make them followers.

        Format your output as a JSON array of objects, each with "title" and "description" keys.
        """
        return await generate_json_response(self.model, prompt)


    # --- STACK 3: COMMERCE STACK LOGIC ---
    async def run_commerce_stack(self, **kwargs: Any) -> Dict:
        """
        Consults the specialist commerce auditor to perform a deep analysis of a specific product.
        """
        product_name = kwargs.get("product_name")
        logger.info(f"Performing a deep commerce audit for product: '{product_name}'")

        # Get tone and country context
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        
        # Update the kwargs with the resolved context for the analyzer
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            "target_country_code": country_context["country_code"],
            "country_name_for_ai": country_context["country_name"],
            "is_global_search": country_context["is_global"],
        })

        # The analyzer is already part of the engine's consciousness. We just consult it.
        return await self.audit_analyzer.run_audit_and_strategy(**kwargs)

    # --- STACK 4: STRATEGY STACK LOGIC ---
    async def run_strategy_stack(self, interest: str, 
                                 user_content_text: Optional[str] = None, 
                                 user_content_url: Optional[str] = None,
                                 user_ip_address: Optional[str] = None,
                                 target_country_name: Optional[str] = None,
                                 product_category: Optional[str] = None,
                                 product_subcategory: Optional[str] = None) -> Dict:
        logger.info(f"Charting a grand strategy for the interest: '{interest}'")
        
        user_tone_instruction = await self._get_user_tone_instruction(user_content_text, user_content_url)
        country_context = await self._resolve_country_context(user_ip_address, target_country_name)

        tasks = {
            "google_keywords": self.google_engine.get_full_keyword_strategy_data(
                interest, country_context["country_code"], country_context["country_name"],
                product_category, product_subcategory
            ),
            "community_pain_points": self.q_and_a_scraper.run_scraping_tasks(
                interest, country_context["country_code"], country_context["country_name"]
            ),
            "keyword_tool_insights": self.trend_tool_scraper.run_scraper_tasks(
                interest, country_context["country_code"], country_context["country_name"],
                product_category, product_subcategory
            ),
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        google_keywords = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        community_pain_points = results[1] if not isinstance(results[1], Exception) else [{"error": str(results[1])}]
        keyword_tool_insights = results[2] if not isinstance(results[2], Exception) else [{"error": str(results[2])}]

        country_phrase = f"for the {country_context['country_name']} market" if not country_context['is_global'] else "for a global audience"
        category_phrase = f" in the '{product_category}' category" if product_category else ""
        if product_category and product_subcategory:
            category_phrase += f" (subcategory: '{product_subcategory}')"
        
        prompt = f"""
        As the goddess Saga, you will now lay down a grand strategy. A hero has come to you with an interest in '{interest}' and seeks to make their mark {country_phrase}{category_phrase}. You have consulted the runes and histories:

        --- MARKET HISTORIES ---
        Google Keyword and Trend Data: {json.dumps(google_keywords, indent=2)}
        Community Pain Points & Questions: {json.dumps(community_pain_points, indent=2)}
        Keyword Tool Insights: {json.dumps(keyword_tool_insights, indent=2)}
        --- END OF HISTORIES ---

        {user_tone_instruction}

        Your task is to prophesize an actionable digital strategy. This prophecy must be clear, wise, and structured.

        Your output MUST be a valid JSON object with the following keys:
        {{
            "keyword_focus": "A detailed prophecy on the primary and long-tail keywords. Which words hold power? Which will gather followers?",
            "content_pillars": "The great themes for their saga. What strategic categories of content will address the people's needs and build a kingdom of organic traffic?",
            "promotion_channels": "Which realms should they travel to spread their message? (e.g., SEO, social media, paid ads, email). Justify your choices.",
            "competitor_analysis_notes": "Prophecies about rivals seen in the data. (Optional, provide notes if data hints at competitors).",
            "overall_strategic_summary": "A concise, actionable summary of the grand strategy. The final verse of this prophecy."
        }}
        """
        return await generate_json_response(self.model, prompt)

    # --- Wrapper methods for Specialist Stacks ---
    # These methods now simply call the pre-initialized modules.

    async def run_arbitrage_stack(self, **kwargs: Any) -> Dict:
        """Consults the specialist price arbitrage finder."""
        product_name = kwargs.get("product_name")
        logger.info(f"Seeking arbitrage opportunities for product: '{product_name}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            "target_country_code": country_context["country_code"],
            "country_name_for_ai": country_context["country_name"],
        })
        return await self.price_arbitrage_finder.find_arbitrage_opportunities(**kwargs)

    async def run_social_selling_stack(self, **kwargs: Any) -> Dict:
        """Consults the specialist social selling strategist."""
        product_name = kwargs.get("product_name")
        logger.info(f"Devising a social selling saga for product: '{product_name}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            "user_ip_address": kwargs.get("user_ip_address"),
            "target_country_name": country_context["country_name"],
        })
        return await self.social_selling_strategist.analyze_social_selling(**kwargs)
        
    async def run_product_route_stack(self, **kwargs: Any) -> Dict:
        """Consults the specialist product route suggester."""
        niche_interest = kwargs.get("niche_interest")
        logger.info(f"Prophesizing a product route for niche: '{niche_interest}'")
        user_tone_instruction = await self._get_user_tone_instruction(kwargs.get("user_content_text"), kwargs.get("user_content_url"))
        country_context = await self._resolve_country_context(kwargs.get("user_ip_address"), kwargs.get("target_country_name"))
        kwargs.update({
            "user_tone_instruction": user_tone_instruction,
            "user_ip_address": kwargs.get("user_ip_address"),
            "target_country_name": country_context["country_name"],
        })
        return await self.product_route_suggester.suggest_product_and_route(**kwargs)
--- END OF FILE backend/engine.py ---