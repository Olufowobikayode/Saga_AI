#!/usr/bin/env python3

import asyncio
import logging
import json
from typing import List, Dict, Any, Callable
from urllib.parse import quote_plus
import argparse
from pprint import pprint

from pytrends.request import TrendReq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
# Configure logging for clean console output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)


# --- SITE CONFIGURATION (The "Brain" of the Scraper) ---
# This is where we define the instructions for each tool.
# "status": "enabled" means we will try to scrape it.
# "status": "protected" means it requires an API key or is too difficult to scrape reliably.
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Ubersuggest": {
        "status": "protected",
        "reason": "Requires login and has strong anti-bot protection. Access via official paid API is recommended.",
    },
    "KeywordTool.io": {
        "status": "protected",
        "reason": "Requires login and has strong anti-bot protection. Their business model is their paid API.",
    },
    "WordStream": {
        "status": "protected",
        "reason": "Complex JS-heavy tool with anti-bot measures.",
    },
    "AnswerThePublic": {
        "status": "enabled",
        "search_url_template": "https://answerthepublic.com/{query}",
        "wait_selector": '.search-vis-list__item',
        "item_selector": '.search-vis-list__item',
        "note": "Fragile due to heavy JS and anti-bot measures. May fail."
    },
    "Keyword Sheeter": {
        "status": "enabled",
        "search_url_template": "https://keywordsheeter.com/",
        "input_selector": '#keyword',
        "submit_selector": 'button[onclick="sheet()"]',
        "wait_selector": '#results_container .kr_word',
        "item_selector": '#results_container .kr_word',
        "note": "Scrapes the initial batch of keywords generated."
    },
    "Soovle": {
        "status": "enabled",
        "search_url_template": "https://soovle.com/?q={query}",
        "wait_selector": '.sv', # The container for suggestions
        "item_selector": '.sv a',
        "note": "Excellent for brainstorming related terms across multiple engines."
    },
    "QuestionDB": {
        "status": "enabled",
        "search_url_template": "https://questiondb.io/query/{query}",
        "wait_selector": 'table.results-table tbody tr',
        "item_selector": 'table.results-table tbody tr td:first-child',
        "note": "Good for finding questions people ask on Reddit."
    },
    "SEO Book": {
        "status": "protected",
        "reason": "Requires a free user login to access the keyword tool.",
    },
    "Bing Keyword Research": {
        "status": "protected",
        "reason": "Requires a Bing Webmaster Tools account and login.",
    },
}


class StandaloneScraper:
    """An enterprise-grade, standalone scraper for keyword and market research."""

    def _get_driver(self) -> webdriver.Chrome:
        """Initializes a headless Chrome browser instance for scraping."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    async def scrape_site(self, site_key: str, query: str, max_items: int = 10) -> Dict:
        """A generic scraper that uses the SITE_CONFIGS to scrape a specific site."""
        config = SITE_CONFIGS[site_key]
        driver = self._get_driver()
        results = []
        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Scraping {site_key}...")
            driver.get(url)

            if config.get("input_selector"):
                input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, config["input_selector"])))
                input_element.send_keys(query)
                if config.get("submit_selector"):
                    driver.find_element(By.CSS_SELECTOR, config["submit_selector"]).click()
            
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"])))
            
            # Allow some time for dynamic content to load
            await asyncio.sleep(3)
            
            elements = driver.find_elements(By.CSS_SELECTOR, config["item_selector"])
            results = [el.text for el in elements[:max_items] if el.text]
            logger.info(f"Successfully found {len(results)} items from {site_key}.")
        except Exception as e:
            logger.error(f"Failed to scrape {site_key}. Error: {e}")
        finally:
            driver.quit()
        
        return { "source": site_key, "keywords": results }

async def get_google_trends_data(interest: str) -> Dict:
    """Uses the reliable pytrends library to get Google Trends data."""
    logger.info("Fetching data from Google Trends API...")
    data = {"related": [], "rising": []}
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        loop = asyncio.get_running_loop()
        
        await loop.run_in_executor(None, lambda: pytrends.build_payload(kw_list=[interest], timeframe='today 3-m'))
        related_queries = await loop.run_in_executor(None, pytrends.related_queries)
        
        top = related_queries.get(interest, {}).get('top')
        rising = related_queries.get(interest, {}).get('rising')

        if top is not None and not top.empty: data["related"] = top['query'].tolist()[:10]
        if rising is not None and not rising.empty: data["rising"] = rising['query'].tolist()[:10]
        logger.info(f"Successfully found {len(data['related']) + len(data['rising'])} trends from Google Trends.")
    except Exception as e:
        logger.error(f"Pytrends API failed: {e}")
    return { "source": "Google Trends", "data": data }


async def main(keyword: str):
    """
    The main orchestrator function. It gathers tasks and runs them in parallel.
    """
    logger.info(f"Starting market research for keyword: '{keyword}'")
    
    scraper = StandaloneScraper()
    tasks = []
    
    # Add scraping tasks for all enabled sites
    for site_key, config in SITE_CONFIGS.items():
        if config["status"] == "enabled":
            tasks.append(scraper.scrape_site(site_key, keyword))
        else:
            logger.warning(f"Skipping '{site_key}': {config['reason']}")

    # Add the reliable Google Trends API task
    tasks.append(get_google_trends_data(keyword))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    final_report = {
        "keyword": keyword,
        "timestamp": datetime.now().isoformat(),
        "intelligence_report": [res for res in results if not isinstance(res, Exception) and (res.get("keywords") or res.get("data"))]
    }
    
    logger.info("--- MARKET RESEARCH REPORT ---")
    pprint(final_report)
    
    # Optionally, save to a file
    with open(f"market_research_{keyword.replace(' ', '_')}.json", "w") as f:
        json.dump(final_report, f, indent=2)
    logger.info(f"Report saved to market_research_{keyword.replace(' ', '_')}.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standalone Market Research Scraper for NicheStack AI")
    parser.add_argument("keyword", type=str, help="The core keyword or niche to research.")
    args = parser.parse_args()
    
    asyncio.run(main(args.keyword))