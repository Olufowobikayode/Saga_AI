# file: backend/trends.py

import asyncio
import logging
import json
from typing import List, Dict, Any
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

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

# --- THE MASTER SITE CONFIGURATION for Keyword Tools ---
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "AnswerThePublic": {
        "status": "enabled",
        "search_url_template": "https://answerthepublic.com/{query}",
        "wait_selector": '.search-vis-list__item',
        "item_selector": '.search-vis-list__item',
    },
    "Keyword Sheeter": {
        "status": "enabled",
        "search_url_template": "https://keywordsheeter.com/",
        "input_selector": '#keyword',
        "submit_selector": 'button[onclick="sheet()"]',
        "wait_selector": '#results_container .kr_word',
        "item_selector": '#results_container .kr_word',
    },
    "Soovle": {
        "status": "enabled",
        "search_url_template": "https://soovle.com/?q={query}",
        "wait_selector": '.sv',
        "item_selector": '.sv a',
    },
    "QuestionDB": {
        "status": "enabled",
        "search_url_template": "https://questiondb.io/query/{query}",
        "wait_selector": 'table.results-table tbody tr',
        "item_selector": 'table.results-table tbody tr td:first-child',
    },
    # --- Protected Sites (documented for future API integration) ---
    "Ubersuggest": {"status": "protected", "reason": "Requires login and has strong anti-bot protection."},
    "KeywordTool.io": {"status": "protected", "reason": "Commercial tool with a paid API."},
    "WordStream": {"status": "protected", "reason": "Commercial tool, heavy JS protection."},
    "SEO Book": {"status": "requires_login", "reason": "Requires a free user login."},
    "Bing Keyword Research": {"status": "requires_login", "reason": "Requires a Bing Webmaster Tools account."},
}

class TrendScraper:
    """A standalone scraper for public keyword research tools."""

    def _get_driver(self) -> webdriver.Chrome:
        """Initializes a headless Chrome browser instance."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    async def _scrape_single_site(self, driver: webdriver.Chrome, site_key: str, query: str, max_items: int = 10) -> Dict:
        """(Internal) Scrapes one site using a shared browser instance."""
        config = SITE_CONFIGS[site_key]
        results = []
        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Navigating to {site_key}...")
            driver.get(url)

            if config.get("input_selector"):
                input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, config["input_selector"])))
                input_element.send_keys(query)
                if config.get("submit_selector"):
                    driver.find_element(By.CSS_SELECTOR, config["submit_selector"]).click()
            
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"])))
            await asyncio.sleep(3) # Allow for dynamic content to load
            
            elements = driver.find_elements(By.CSS_SELECTOR, config["item_selector"])
            results = [el.text for el in elements[:max_items] if el.text]
            logger.info(f"-> Found {len(results)} keywords from {site_key}.")
        except Exception as e:
            logger.error(f"-> Failed to scrape {site_key}. Error: {e}")
        
        return { "source": site_key, "keywords": results }

    async def run_scraper_tasks(self, keyword: str) -> List[Dict]:
        """
        The main public method for this module. It runs scrapers for all 'enabled' tools.
        """
        logger.info(f"--- Starting Keyword Tool Scraper for '{keyword}' ---")
        driver = self._get_driver()
        tasks = []

        for site_key, config in SITE_CONFIGS.items():
            if config["status"] == "enabled":
                tasks.append(self._scrape_single_site(driver, site_key, keyword))
            else:
                logger.warning(f"Skipping '{site_key}': {config['reason']}")
        
        try:
            scraped_data = await asyncio.gather(*tasks)
        finally:
            logger.info("All scraping tasks complete. Closing browser.")
            driver.quit()

        return [result for result in scraped_data if result.get('keywords')]

async def main(keyword: str):
    """Orchestrator for running this script from the command line."""
    scraper = TrendScraper()
    scraped_data = await scraper.run_scraper_tasks(keyword)
    
    final_report = {
        "keyword": keyword,
        "timestamp": datetime.now().isoformat(),
        "keyword_tool_report": scraped_data
    }
    
    logger.info("--- KEYWORD TOOL REPORT ---")
    pprint(final_report)
    
    filename = f"keyword_tool_report_{keyword.replace(' ', '_')}.json"
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    logger.info(f"--- REPORT SAVED TO {filename} ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standalone Keyword Tool Scraper for NicheStack AI")
    parser.add_argument("keyword", type=str, help="The core keyword or niche to research.")
    args = parser.parse_args()
    asyncio.run(main(args.keyword))