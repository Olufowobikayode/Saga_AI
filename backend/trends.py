# --- START OF REFACTORED FILE backend/trends.py ---
import asyncio
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import argparse
from pprint import pprint
import random

from playwright.async_api import async_playwright, BrowserContext
from fake_useragent import UserAgent

from backend.cache import seer_cache, generate_cache_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Soovle": {
        "status": "enabled",
        "reason": "Provides a unique, multi-source view of top-level search suggestions.",
        "search_url_template": "https://soovle.com/?q={query}",
        "item_selector": ".sv a",
    },
    "QuestionDB": {
        "status": "enabled",
        "reason": "A valuable source for discovering the raw questions people ask about a topic.",
        "search_url_template": "https://questiondb.io/query/{query}",
        "item_selector": "table.results-table tr > td:first-child",
    },
}

class TrendScraper:
    """
    An aspect of Saga that divines wisdom from public keyword research tools, now powered by Playwright.
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
        
        logger.info("Summoning the Playwright browser spirit for TrendScraper...")
        self._playwright_instance = await async_playwright().start()
        self._browser = await self._playwright_instance.chromium.launch(headless=True)
        return self._browser

    async def _create_stealth_context(self) -> BrowserContext:
        """Creates a new, isolated browser context with stealth properties."""
        browser = await self._get_browser()
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        
        context = await browser.new_context(
            user_agent=user_agent,
            java_script_enabled=True,
            viewport={'width': 1280, 'height': 800},
            locale='en-US'
        )
        return context

    async def _divine_from_realm(self, site_key: str, query: str, max_items: int = 10) -> Dict:
        """Gazes into a single keyword realm using a dedicated Playwright context."""
        config = SITE_CONFIGS[site_key]
        results = []
        url = config["search_url_template"].format(query=quote_plus(query))
        logger.info(f"Gazing into the {site_key} realm for '{query}'...")

        context = await self._create_stealth_context()
        page = None
        try:
            page = await context.new_page()
            await page.goto(url, timeout=30000, wait_until='domcontentloaded')
            
            await page.wait_for_selector(config['item_selector'], timeout=20000)
            await page.wait_for_timeout(random.uniform(3100, 4500))

            item_locators = page.locator(config['item_selector'])
            
            count = min(await item_locators.count(), max_items)
            for i in range(count):
                text = await item_locators.nth(i).inner_text()
                if text and text.strip():
                    results.append(text.strip())

            logger.info(f"-> The {site_key} realm revealed {len(results)} keyword chants for '{query}'.")
        except Exception as e:
            logger.warning(f"-> The mists of {site_key} obscured my vision for '{query}'. Error: {e}")
        finally:
            if page: await page.close()
            if context: await context.close()
            
        return {"source": site_key, "keywords": results}

    async def run_scraper_tasks(self, keyword: str,
                                country_code: Optional[str] = None, country_name: Optional[str] = None,
                                product_category: Optional[str] = None, product_subcategory: Optional[str] = None) -> List[Dict]:
        """
        The main public rite for this seer. It orchestrates divination from all 'enabled' keyword realms.
        """
        search_query = keyword
        if product_category: search_query += f' "{product_category}"'
        if product_subcategory: search_query += f' "{product_subcategory}"'

        cache_key = generate_cache_key("run_scraper_tasks", query=search_query, country=country_code)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        logger.info(f"--- Divining keyword trends for '{search_query}' (Realm: {country_name or 'Global'}) ---")
        
        tasks = []
        for site_key, config in SITE_CONFIGS.items():
            if config["status"] == "enabled":
                tasks.append(self._divine_from_realm(site_key, search_query))
            else:
                logger.warning(f"Skipping the realm of '{site_key}': {config['reason']}")
        
        try:
            raw_scraped_data = await asyncio.gather(*tasks, return_exceptions=True)
            scraped_data = [res for res in raw_scraped_data if not isinstance(res, Exception) and res.get('keywords')]
            seer_cache.set(cache_key, scraped_data, ttl_seconds=7200)
            return scraped_data
        except Exception as e:
            logger.critical(f"A great disturbance prevented the divination of trends: {e}")
            return []

# The standalone test function
async def main(keyword: str):
    import time
    scraper = TrendScraper()
    print("\n--- Divining trends ---")
    start_time = time.time()
    scraped_data = await scraper.run_scraper_tasks(keyword)
    duration = time.time() - start_time
    final_report = {
        "keyword_divined": keyword, "duration_seconds": f"{duration:.2f}",
        "trend_report": scraped_data
    }
    pprint(final_report)

    if scraper._browser:
        await scraper._browser.close()
    if scraper._playwright_instance:
        await scraper._playwright_instance.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A standalone seer for divining keyword trends.")
    parser.add_argument("keyword", type=str, help="The core keyword or niche to divine.")
    args = parser.parse_args()
    asyncio.run(main(args.keyword))

# --- END OF REFACTORED FILE backend/trends.py ---