import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import argparse
from pprint import pprint
from datetime import datetime
import random # ### ENHANCEMENT: Import for randomized delays

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# ### ENHANCEMENT: Import libraries for scraper evasion
from selenium_stealth import stealth
from fake_useragent import UserAgent

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

# --- SAGA'S SCROLL OF KEYWORD REALMS ---
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Soovle": {
        "status": "enabled",
        "reason": "Provides a unique, multi-source view of top-level search suggestions.",
        "search_url_template": "https://soovle.com/?q={query}",
        "wait_selector": '.sv',
        "item_selector": '.sv a',
    },
    "QuestionDB": {
        "status": "enabled",
        "reason": "A valuable source for discovering the raw questions people ask about a topic.",
        "search_url_template": "https://questiondb.io/query/{query}",
        "wait_selector": 'table.results-table tbody tr',
        "item_selector": 'table.results-table tbody tr td:first-child',
    },
    "Ubersuggest": {"status": "protected", "reason": "Requires login and has strong anti-bot protection."},
    "KeywordTool.io": {"status": "protected", "reason": "A powerful commercial tool with a paid API, best accessed that way."},
    "AnswerThePublic": {"status": "protected", "reason": "This realm is now guarded more heavily; its whispers are better gathered by the KeywordEngine API."},
}

class TrendScraper:
    """
    An aspect of Saga that divines wisdom from public keyword research tools.
    It listens to the 'chants of the seekers' to understand what mortals are searching for.
    This Seer is now enhanced with stealth capabilities to appear more human.
    """

    def __init__(self):
        # ### ENHANCEMENT: Initialize the UserAgent object once.
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

    def _get_driver(self) -> webdriver.Chrome:
        """Initializes a headless, stealthy Chrome spirit for its journey."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # ### ENHANCEMENT 1: Use a randomized, real-world user agent for each request.
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")

        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # ### ENHANCEMENT 2: Apply selenium-stealth patches to the driver.
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )
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

            await asyncio.to_thread(WebDriverWait(driver, 20).until(
                                   EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"]))))
            
            # ### ENHANCEMENT 3: Use randomized delays to better mimic human behavior.
            await asyncio.sleep(random.uniform(3.1, 4.5))
            
            elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["item_selector"])
            
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
        """
        search_query = keyword
        if product_category:
            search_query += f' "{product_category}"'
        if product_subcategory:
            search_query += f' "{product_subcategory}"'

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
            
            scraped_data = await asyncio.gather(*tasks, return_exceptions=True)
            scraped_data = [res for res in scraped_data if not isinstance(res, Exception) and res.get('keywords')]

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
    """A standalone ritual to test the TrendScraper's powers."""
    sample_country_name = "Germany"
    sample_category = "Software Development"

    scraper = TrendScraper()
    scraped_data = await scraper.run_scraper_tasks(keyword, country_name=sample_country_name, product_category=sample_category)
    
    final_report = {
        "keyword_divined": keyword,
        "context": {
            "country_name": sample_country_name,
            "product_category": sample_category,
        },
        "timestamp": datetime.now().isoformat(),
        "trend_report": scraped_data
    }
    
    logger.info("--- SCROLL OF TRENDING KEYWORDS ---")
    pprint(final_report)
    
    filename = f"keyword_trend_report_{keyword.replace(' ', '_')}.json"
    try:
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        logger.info(f"--- Scroll of Trending Keywords has been inscribed to {filename} ---")
    except IOError as e:
        logger.error(f"Failed to inscribe the scroll ({filename}): {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A standalone seer for divining keyword trends.")
    parser.add_argument("keyword", type=str, help="The core keyword or niche to divine.")
    args = parser.parse_args()
    asyncio.run(main(args.keyword))