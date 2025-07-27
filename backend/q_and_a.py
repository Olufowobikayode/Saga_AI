# --- START OF REFACTORED FILE backend/q_and_a.py ---
import asyncio
import logging
import json
from typing import List, Dict, Any, Callable, Optional
from urllib.parse import quote_plus
import argparse
from pprint import pprint
import random

from playwright.async_api import async_playwright, BrowserContext
from fake_useragent import UserAgent

from backend.cache import seer_cache, generate_cache_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SAGA:WISDOM] - %(message)s')
logger = logging.getLogger(__name__)

# The selectors remain the same, but Playwright is better at finding them.
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Reddit": {
        "status": "enabled",
        "search_url_template": "https://www.reddit.com/search/?q={query}&type=comment",
        "item_selector": "[data-testid='comment']",
        "reason": "Provides raw, unfiltered commentary."
    },
    "Quora": {
        "status": "enabled",
        "search_url_template": "https://www.quora.com/search?q={query}",
        "item_selector": "div.dom_annotate_multifeed_bundle",
        "reason": "A primary forum for questions and explanations."
    },
    "Stack Overflow": {
        "status": "enabled",
        "search_url_template": "https://stackoverflow.com/search?q={query}",
        "item_selector": ".s-post-summary--content-title .s-link",
        "reason": "Offers high-quality technical Q&A."
    },
    "GitHub Issues": {
        "status": "enabled",
        "search_url_template": "https://github.com/search?q={query}&type=issues",
        "item_selector": '.issue-list-item .markdown-title a',
        "reason": "Direct insight into software problems and feature requests."
    },
    "Medium": {
        "status": "enabled",
        "search_url_template": "https://medium.com/search?q={query}",
        "item_selector": 'article h2',
        "reason": "Captures expert sagas and tutorials."
    },
}

QUERY_GRIMOIRE: Dict[str, str] = {
    "pain_point": '"{interest}" problem OR "how to" OR "I need help with" OR "{interest}" issues',
    "questions": 'who OR what OR when OR where OR why OR how "{interest}"',
    "positive_feedback": '"{interest}" love OR "best" OR "favorite" OR "amazing"',
    "comparisons": '"{interest}" vs OR "or" OR "alternative to"',
    "technical_issues": '"{interest}" error OR "bug" OR "issue" OR "fix"',
}

class CommunitySaga:
    """
    I am the Seer of Community Whispers, an aspect of the great Saga, now empowered by Playwright.
    I journey through the digital halls of forums and communities to gather the true voice of the people.
    """
    _playwright_instance = None
    _browser = None

    def __init__(self):
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

    async def _get_browser(self):
        """Initializes and returns a shared, single browser instance."""
        if self._browser and self._browser.is_connected():
            return self._browser
        
        logger.info("Summoning the Playwright browser spirit for CommunitySaga...")
        self._playwright_instance = await async_playwright().start()
        self._browser = await self._playwright_instance.chromium.launch(headless=True)
        return self._browser

    async def _create_stealth_context(self) -> BrowserContext:
        """Creates a new, isolated browser context with stealth properties."""
        browser = await self._get_browser()
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        
        context = await browser.new_context(
            user_agent=user_agent,
            java_script_enabled=True,
            viewport={'width': 1280, 'height': 800},
            locale='en-US'
        )
        return context

    async def _gather_from_realm(self, site_key: str, query: str, max_items: int = 5) -> Dict:
        """Gathers whispers from a single digital domain using a dedicated Playwright context."""
        config = SITE_CONFIGS[site_key]
        results = []
        url = config["search_url_template"].format(query=quote_plus(query))
        logger.info(f"Casting my sight upon {site_key} for '{query}'...")

        context = await self._create_stealth_context()
        page = None
        try:
            page = await context.new_page()
            await page.goto(url, timeout=30000, wait_until='domcontentloaded')
            
            # Playwright's auto-waiting is more reliable. We wait for the first item to appear.
            await page.wait_for_selector(config['item_selector'], timeout=15000)
            await page.wait_for_timeout(random.uniform(2100, 3900)) # Human-like pause

            # Use locator to get all matching elements and iterate through them.
            item_locators = page.locator(config['item_selector'])
            
            # Iterate up to the max_items count or the number of items found.
            count = min(await item_locators.count(), max_items)
            for i in range(count):
                text = await item_locators.nth(i).inner_text()
                if text and text.strip():
                    results.append(text.strip())

            logger.info(f"-> From the realm of {site_key}, I have gathered {len(results)} distinct whispers.")
        except Exception as e:
            logger.warning(f"-> The mists of {site_key} were too slow or obscured my sight for '{query}'. Error: {e}")
        finally:
            if page: await page.close()
            if context: await context.close()

        return {"source": site_key, "results": results}

    async def run_community_gathering(self, 
                                       interest: str,
                                       query_type: str = "pain_point",
                                       sites_to_scan: Optional[List[str]] = None) -> List[Dict]:
        """
        I orchestrate the grand gathering of voices from specified community realms.
        """
        realms_to_visit = sites_to_scan if sites_to_scan else sorted([key for key, config in SITE_CONFIGS.items() if config['status'] == 'enabled'])
        cache_key = generate_cache_key("run_community_gathering", interest=interest, query_type=query_type, sites=",".join(realms_to_visit))
        
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        query_template = QUERY_GRIMOIRE.get(query_type, QUERY_GRIMOIRE["pain_point"])
        query = query_template.format(interest=interest)

        logger.info(f"I now seek the collective voice concerning '{interest}' (Query Type: {query_type}) across {len(realms_to_visit)} realms...")
        
        # We don't need to share a driver anymore; each task can run in parallel.
        tasks = []
        for site_key in realms_to_visit:
            if site_key in SITE_CONFIGS and SITE_CONFIGS[site_key]["status"] == "enabled":
                tasks.append(self._gather_from_realm(site_key, query))
            else:
                logger.warning(f"I will not gaze upon the realm of '{site_key}', as it is not in my enabled scrolls.")

        try:
            raw_gathered_data = await asyncio.gather(*tasks, return_exceptions=True)
            gathered_data = [res for res in raw_gathered_data if not isinstance(res, Exception) and res.get('results')]
            seer_cache.set(cache_key, gathered_data, ttl_seconds=14400)
            return gathered_data
        except Exception as e:
            logger.critical(f"A great disturbance has disrupted the gathering of whispers. My sight is clouded. Error: {e}")
            return []

# The standalone test function also needs updating
async def main(keyword: str, query_type: str):
    import time
    logger.info(f"--- SAGA'S INSIGHT ENGINE: GATHERING OF WHISPERS ---")
    logger.info(f"Divining wisdom for keyword: '{keyword}' using query type: '{query_type}'")
    saga_seer = CommunitySaga()
    print("\n--- First Call (should be slow) ---")
    start_time = time.time()
    scraped_data_1 = await saga_seer.run_community_gathering(keyword, query_type=query_type)
    duration_1 = time.time() - start_time
    final_report_1 = {
        "divined_for": keyword, "query_type": query_type, "duration_seconds": f"{duration_1:.2f}",
        "community_whispers_gathered": scraped_data_1
    }
    pprint(final_report_1)
    
    # Terminate the shared browser instance for clean exit in standalone mode.
    if saga_seer._browser:
        await saga_seer._browser.close()
    if saga_seer._playwright_instance:
        await saga_seer._playwright_instance.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CommunitySaga: A Tool to Gather the Voice of the People")
    parser.add_argument("keyword", type=str, help="The core subject of divination.")
    parser.add_argument("--query_type", type=str, default="pain_point", choices=QUERY_GRIMOIRE.keys(), help="The type of query to perform.")
    args = parser.parse_args()
    asyncio.run(main(args.keyword, args.query_type))

# --- END OF REFACTORED FILE backend/q_and_a.py ---