import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import argparse
from pprint import pprint
from datetime import datetime
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from selenium_stealth import stealth
from fake_useragent import UserAgent

from backend.cache import seer_cache, generate_cache_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

# ### ENHANCEMENT: Upgraded selectors to be more robust, using XPath where beneficial.
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Soovle": {
        "status": "enabled",
        "selector_type": "xpath",
        "reason": "Provides a unique, multi-source view of top-level search suggestions.",
        "search_url_template": "https://soovle.com/?q={query}",
        # This XPath finds any element with the class 'sv', which is more direct.
        "wait_selector": "//*[@class='sv']",
        "item_selector": "//*[@class='sv']/a",
    },
    "QuestionDB": {
        "status": "enabled",
        "selector_type": "xpath",
        "reason": "A valuable source for discovering the raw questions people ask about a topic.",
        "search_url_template": "https://questiondb.io/query/{query}",
        # This XPath is more resilient to changes in table structure.
        "wait_selector": "//table[contains(@class, 'results-table')]//tr",
        "item_selector": "//table[contains(@class, 'results-table')]//tr/td[1]",
    },
}

class TrendScraper:
    """
    An aspect of Saga that divines wisdom from public keyword research tools.
    It listens to the 'chants of the seekers' to understand what mortals are searching for.
    This Seer is now enhanced with stealth, caching, and robust selectors.
    """

    def __init__(self):
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

    def _get_driver(self) -> webdriver.Chrome:
        # ... (This method remains unchanged)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
            return driver
        except WebDriverException as e:
            logger.error(f"The Chrome spirit failed to materialize: {e}. Ensure its essence and path are known.")
            raise
        except Exception as e:
            logger.error(f"An unknown enchantment disrupted the summoning of the Chrome spirit: {e}")
            raise

    async def _divine_from_realm(self, driver: webdriver.Chrome, site_key: str, query: str, max_items: int = 10) -> Dict:
        """(Internal) Gazes into a single keyword realm using a shared Chrome spirit."""
        config = SITE_CONFIGS[site_key]
        results = []
        
        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Gazing into the {site_key} realm for '{query}'...")
            await asyncio.to_thread(driver.get, url)

            # ### ENHANCEMENT: Use the correct By method based on selector_type
            by_method = By.XPATH if config['selector_type'] == 'xpath' else By.CSS_SELECTOR

            await asyncio.to_thread(WebDriverWait(driver, 20).until(
                                   EC.presence_of_all_elements_located((by_method, config["wait_selector"]))))
            
            await asyncio.sleep(random.uniform(3.1, 4.5))
            
            elements = await asyncio.to_thread(driver.find_elements, by_method, config["item_selector"])
            
            for el in elements[:max_items]:
                text = await asyncio.to_thread(lambda: el.text)
                if text:
                    results.append(text)
            logger.info(f"-> The {site_key} realm revealed {len(results)} keyword chants for '{query}'.")
        except TimeoutException:
            logger.warning(f"-> The mists of {site_key} obscured my vision for '{query}' (Timeout).")
        except NoSuchElementException:
            logger.warning(f"-> The runes of {site_key} have shifted for '{query}'; the patterns I seek are gone.")
        except Exception as e:
            logger.error(f"-> A powerful ward protects the {site_key} realm for '{query}'. Error: {e}")
        
        return { "source": site_key, "keywords": results }

    async def run_scraper_tasks(self, keyword: str,
                                country_code: Optional[str] = None, country_name: Optional[str] = None,
                                product_category: Optional[str] = None, product_subcategory: Optional[str] = None) -> List[Dict]:
        """
        The main public rite for this seer. It orchestrates divination from all 'enabled' keyword realms.
        This operation is cached to prevent excessive scraping.
        """
        search_query = keyword
        if product_category:
            search_query += f' "{product_category}"'
        if product_subcategory:
            search_query += f' "{product_subcategory}"'

        cache_key = generate_cache_key("run_scraper_tasks", query=search_query, country=country_code)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        logger.info(f"--- Divining keyword trends for '{search_query}' (Realm: {country_name or 'Global'}) ---")
        driver = None
        scraped_data = []
        try:
            driver = self._get_driver()
            tasks = []

            for site_key, config in SITE_CONFIGS.items():
                if config["status"] == "enabled":
                    tasks.append(self._divine_from_realm(driver, site_key, search_query))
                else:
                    logger.warning(f"Skipping the realm of '{site_key}': {config['reason']}")
            
            raw_scraped_data = await asyncio.gather(*tasks, return_exceptions=True)
            scraped_data = [res for res in raw_scraped_data if not isinstance(res, Exception) and res.get('keywords')]

            seer_cache.set(cache_key, scraped_data, ttl_seconds=7200)

        except Exception as e:
            logger.critical(f"A great disturbance prevented the divination of trends: {e}")
            if driver:
                await asyncio.to_thread(driver.quit)
            return []
        finally:
            if driver:
                logger.info("The divination of trends is complete. The Chrome spirit is dismissed.")
                await asyncio.to_thread(driver.quit)

        return scraped_data

async def main(keyword: str):
    # ... (This main block for testing remains unchanged)
    import time
    sample_country_name = "Germany"
    sample_category = "Software Development"
    scraper = TrendScraper()
    print("\n--- First Call (should be slow) ---")
    start_time = time.time()
    scraped_data_1 = await scraper.run_scraper_tasks(keyword, country_name=sample_country_name, product_category=sample_category)
    duration_1 = time.time() - start_time
    final_report = {
        "keyword_divined": keyword, "duration_seconds": f"{duration_1:.2f}",
        "context": {"country_name": sample_country_name, "product_category": sample_category},
        "trend_report": scraped_data_1
    }
    pprint(final_report)
    print("\n--- Second Call (should be instant) ---")
    start_time_2 = time.time()
    scraped_data_2 = await scraper.run_scraper_tasks(keyword, country_name=sample_country_name, product_category=sample_category)
    duration_2 = time.time() - start_time_2
    if duration_2 < 0.1 and len(scraped_data_1) == len(scraped_data_2):
        print(f"\n[SUCCESS] Caching is working! Second call took only {duration_2:.4f} seconds.")
    else:
        print(f"\n[FAILURE] Caching is not working correctly. Second call took {duration_2:.2f} seconds.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A standalone seer for divining keyword trends.")
    parser.add_argument("keyword", type=str, help="The core keyword or niche to divine.")
    args = parser.parse_args()
    asyncio.run(main(args.keyword))