import asyncio
import logging
import os
import json
from typing import Dict, Any, Optional
import aiohttp
import pandas as pd
from pytrends.request import TrendReq
from concurrent.futures import ThreadPoolExecutor

# ### FIX: Import the caching utilities
from backend.cache import seer_cache, generate_cache_key

logger = logging.getLogger(__name__)

class KeywordRuneKeeper:
    """
    The keeper of keyword runes, an aspect of Saga that deciphers the intent
    of seekers through the APIs of Google Trends and KeywordTool.io.
    This Seer is now enhanced with caching to conserve its power (API calls).
    """
    def __init__(self):
        self.keywordtool_api_key = os.environ.get("KEYWORDTOOL_IO_API_KEY")
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def decipher_from_keywordtool_io(self, keyword: str, country_code: Optional[str] = None, currency: Optional[str] = None) -> Dict:
        """Reads the runes from the KeywordTool.io API."""
        if not self.keywordtool_api_key:
            logger.warning("The runes of KeywordTool.io are sealed (API key not provided).")
            return {}

        base_url = "https://api.keywordtool.io/v2/search/find-keywords"
        params = {
            "apikey": self.keywordtool_api_key,
            "keyword": keyword,
            "metrics": "true",
            "metrics_location": country_code if country_code else "2840", # Default to US
            "metrics_language": "en",
            "metrics_network": "google",
            "metrics_currency": currency if currency else "USD",
            "output": "json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    # We only care about the 'results' part of the prophecy
                    return data.get("results", {})
        except aiohttp.ClientError as e:
            logger.error(f"The KeywordTool.io runes were unreadable: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"An unexpected disturbance occurred while reading the KeywordTool.io runes: {e}")
            return {"error": str(e)}

    async def divine_from_google_trends(self, keyword: str, country_code: Optional[str] = None) -> Dict:
        """Divines the future of a keyword using the Google Trends API."""
        loop = asyncio.get_running_loop()
        
        def get_trends():
            # Pytrends is synchronous, so we run it in a thread pool
            pytrends = TrendReq(hl='en-US', tz=360)
            geo = country_code.upper() if country_code else ''
            
            try:
                pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo=geo, gprop='')
                
                interest_over_time_df = pytrends.interest_over_time()
                related_queries = pytrends.related_queries()
                
                # Convert DataFrames to JSON-serializable dictionaries
                interest_data = interest_over_time_df.to_dict('index') if not interest_over_time_df.empty else {}
                
                rising_queries = {}
                if related_queries.get(keyword, {}).get('rising') is not None:
                    rising_df = related_queries[keyword]['rising']
                    rising_queries = rising_df.to_dict('records')

                return {
                    "interest_over_time": interest_data,
                    "rising": [q['query'] for q in rising_queries[:5]] # Top 5 rising queries
                }
            except Exception as e:
                # This can happen if there's not enough data for the trend
                logger.warning(f"Google Trends could not divine a fate for '{keyword}': {e}")
                return {"error": f"Not enough trend data for '{keyword}'.", "details": str(e)}

        try:
            return await loop.run_in_executor(self.executor, get_trends)
        except Exception as e:
            logger.error(f"A critical error occurred in the Google Trends divination rite: {e}")
            return {"error": "Google Trends divination failed.", "details": str(e)}

    async def get_full_keyword_runes(self, keyword: str, country_code: Optional[str] = None, currency: Optional[str] = None) -> Dict:
        """
        Gathers all keyword runes from all available sources.
        This is the primary public method and is cached for 6 hours.
        """
        # ### ENHANCEMENT: Implement caching for this expensive operation.
        cache_key = generate_cache_key("get_full_keyword_runes", keyword=keyword, country=country_code, currency=currency)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        logger.info(f"Reading the full set of keyword runes for '{keyword}'...")
        
        tasks = {
            "google_trends": self.divine_from_google_trends(keyword, country_code),
            "keywordtool_io": self.decipher_from_keywordtool_io(keyword, country_code, currency)
        }
        
        results = await asyncio.gather(*tasks.values())
        
        final_results = {key: res for key, res in zip(tasks.keys(), results)}

        # ### ENHANCEMENT: Set the result in the cache with a medium TTL (6 hours = 21600 seconds).
        seer_cache.set(cache_key, final_results, ttl_seconds=21600)

        return final_results

# Standalone execution for testing
async def main():
    """A standalone ritual to test the Rune Keeper's powers."""
    import time
    from dotenv import load_dotenv
    load_dotenv()

    keeper = KeywordRuneKeeper()
    keyword_to_test = "ai agent"

    print(f"\n--- Testing Keyword Rune Keeper for '{keyword_to_test}' ---")
    
    print("\n--- First Call (should be slow, requires API calls) ---")
    start_time = time.time()
    runes_1 = await keeper.get_full_keyword_runes(keyword_to_test, country_code="US")
    duration_1 = time.time() - start_time
    print(json.dumps(runes_1, indent=2))
    print(f"First call duration: {duration_1:.2f} seconds.")

    print("\n--- Second Call (should be instant from cache) ---")
    start_time_2 = time.time()
    runes_2 = await keeper.get_full_keyword_runes(keyword_to_test, country_code="US")
    duration_2 = time.time() - start_time_2
    print(f"Second call duration: {duration_2:.4f} seconds.")

    if duration_2 < 0.1 and runes_1 == runes_2:
        print("\n[SUCCESS] Caching is working as expected!")
    else:
        print("\n[FAILURE] Caching is not working correctly.")

if __name__ == "__main__":
    asyncio.run(main())