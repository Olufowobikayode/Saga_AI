--- START OF FILE backend/trends.py ---
import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import argparse
from pprint import pprint
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

# --- SAGA'S SCROLL OF KEYWORD REALMS ---
# Saga's Insight: These realms reveal the questions mortals ask of the digital ether.
# By listening here, we can understand the currents of interest and need.
# Note: These public tools are often guarded. Their reliability can shift like the tides.
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
    # --- Protected Realms (Documented for potential future API integration) ---
    # Saga's Decree: These realms are heavily fortified or demand tribute (paid APIs).
    # We shall not waste our energy here, but remember them for a time when we may hold their keys.
    "Ubersuggest": {"status": "protected", "reason": "Requires login and has strong anti-bot protection."},
    "KeywordTool.io": {"status": "protected", "reason": "A powerful commercial tool with a paid API, best accessed that way."},
    "AnswerThePublic": {"status": "protected", "reason": "This realm is now guarded more heavily; its whispers are better gathered by the KeywordEngine API."},
}

class TrendScraper:
    """
    An aspect of Saga that divines wisdom from public keyword research tools.
    It listens to the 'chants of the seekers' to understand what mortals are searching for.
    """

    def _get_driver(self) -> webdriver.Chrome:
        """Initializes a headless Chrome spirit for its journey."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            logger.error(f"The Chrome spirit failed to materialize: {e}. Ensure its essence and path are known.")
            raise
        except Exception as e:
            logger.error(f"An unknown enchantment disrupted the summoning of the Chrome spirit: {e}")
            raise

    async def _divine_from_realm(self, driver: webdriver.Chrome, site_key: str, query: str, max_items: int = 10,
                                 country_name: Optional[str] = None, product_category: Optional[str] = None) -> Dict:
        """(Internal) Gazes into a single keyword realm using a shared Chrome spirit."""
        config = SITE_CONFIGS[site_key]
        results = []
        
        context_parts = []
        if country_name: context_parts.append(f"Realm: {country_name}")
        if product_category: context_parts.append(f"Domain: {product_category}")
        context_suffix = f" ({', '.join(context_parts)})" if context_parts else ""

        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Gazing into the {site_key} realm for '{query}'{context_suffix}...")
            await asyncio.to_thread(driver.get, url)

            await asyncio.to_thread(WebDriverWait(driver, 20).until(
                                   EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"]))))
            await asyncio.sleep(3) # Allow the realm's echoes to settle.
            
            elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["item_selector"])
            
            for el in elements[:max_items]:
                text = await asyncio.to_thread(lambda: el.text)
                if text:
                    results.append(text)
            logger.info(f"-> The {site_key} realm revealed {len(results)} keyword chants{context_suffix}.")
        except TimeoutException:
            logger.warning(f"-> The mists of {site_key} obscured my vision (Timeout){context_suffix}.")
        except NoSuchElementException:
            logger.warning(f"-> The runes of {site_key} have shifted; the patterns I seek are gone{context_suffix}.")
        except Exception as e:
            logger.error(f"-> A powerful ward protects the {site_key} realm{context_suffix}. Error: {e}")
        
        return { "source": site_key, "keywords": results }

    async def run_scraper_tasks(self, keyword: str,
                                country_code: Optional[str] = None, country_name: Optional[str] = None,
                                product_category: Optional[str] = None, product_subcategory: Optional[str] = None) -> List[Dict]:
        """
        The main public rite for this seer. It orchestrates divination from all 'enabled' keyword realms.
        """
        logger.info(f"--- Divining keyword trends for '{keyword}' (Realm: {country_name or 'Global'}) ---")
        driver = None
        scraped_data = []
        try:
            driver = self._get_driver()
            tasks = []

            for site_key, config in SITE_CONFIGS.items():
                if config["status"] == "enabled":
                    tasks.append(self._divine_from_realm(driver, site_key, keyword, country_name=country_name, product_category=product_category))
                else:
                    logger.warning(f"Skipping the realm of '{site_key}': {config['reason']}")
            
            scraped_data = await asyncio.gather(*tasks, return_exceptions=True)
            # Present only the wisdom that was successfully gathered.
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
--- END OF FILE backend/trends.py ---