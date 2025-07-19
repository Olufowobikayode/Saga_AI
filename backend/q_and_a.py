#!/usr/bin/env python3

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


# --- THE MASTER SITE CONFIGURATION ---
# This is the "brain" of the scraper. Status can be 'enabled', 'protected', or 'requires_login'.
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    # General Q&A and Community Platforms
    "Quora": {"status": "enabled", "search_url_template": "https://www.quora.com/search?q={query}", "wait_selector": '.qu-userText', "item_selector": '.qu-userText'},
    "Reddit": {"status": "enabled", "search_url_template": "https://www.reddit.com/search/?q={query}&type=comment", "wait_selector": '[data-testid="comment"]', "item_selector": '[data-testid="comment"] > div > div'},
    "Stack Exchange": {"status": "enabled", "search_url_template": "https://stackexchange.com/search?q={query}", "wait_selector": '.s-post-summary--content-title', "item_selector": '.s-post-summary--content-title .s-link'},
    "Medium": {"status": "enabled", "search_url_template": "https://medium.com/search?q={query}", "wait_selector": 'article h2', "item_selector": 'article h2'},
    "Answers.com": {"status": "protected", "reason": "Heavy JS, CAPTCHA protection."},
    "Ask.fm": {"status": "protected", "reason": "Login-centric, not ideal for broad scraping."},
    "4chan": {"status": "protected", "reason": "Highly volatile, CAPTCHA protected."},
    
    # Academic and Educational Q&A Sites
    "Stack Overflow": {"status": "enabled", "search_url_template": "https://stackoverflow.com/search?q={query}", "wait_selector": '#mainbar', "item_selector": '.s-post-summary--content .s-post-summary--content-title a'},
    "Brainly": {"status": "protected", "reason": "Requires login and has strong anti-bot measures."},
    "Chegg": {"status": "requires_login", "reason": "All valuable content is behind a paywall."},
    "ResearchGate": {"status": "requires_login", "reason": "Academic network requiring login."},
    "Academia.edu": {"status": "requires_login", "reason": "Academic network requiring login."},
    
    # Technical and Programming Q&A Sites
    "GitHub Issues": {"status": "enabled", "search_url_template": "https://github.com/search?q={query}&type=issues", "wait_selector": '.issue-list-item', "item_selector": '.issue-list-item .markdown-title a'},
    "Dev.to": {"status": "enabled", "search_url_template": "https://dev.to/search?q={query}", "wait_selector": 'article', "item_selector": 'h2.crayons-story__title a'},
    "XDA Developers": {"status": "enabled", "search_url_template": "https://xdaforums.com/search/?q={query}", "wait_selector": '.structItem-title', "item_selector": '.structItem-title > a'},
    "Experts-Exchange": {"status": "requires_login", "reason": "Expert network behind a paywall."},
    
    # Niche and Hobbyist Forums
    "Bodybuilding.com": {"status": "enabled", "search_url_template": "https://forum.bodybuilding.com/search.php?s=&q={query}&search_type=post", "wait_selector": ".search-result-title", "item_selector": ".search-result-text"},
    "TripAdvisor": {"status": "enabled", "search_url_template": "https://www.tripadvisor.com/Search?q={query}", "wait_selector": ".result-title", "item_selector": ".result-title"},
    "Warrior Forum": {"status": "enabled", "search_url_template": "https://www.warriorforum.com/search.php?q={query}", "wait_selector": 'h3.search-result-title', "item_selector": 'h3.search-result-title a'},
    "FlyerTalk": {"status": "protected", "reason": "Complex forum structure with potential bot blocks."},
}


class UniversalScraper:
    """An enterprise-grade, config-driven scraper for market intelligence."""

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

    async def scrape_site(self, driver: webdriver.Chrome, site_key: str, query: str, max_items: int = 5) -> Dict:
        """Scrapes a single site using a shared, pre-initialized browser instance."""
        config = SITE_CONFIGS[site_key]
        results = []
        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Navigating to {site_key}...")
            driver.get(url)
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"]))
            )
            
            await asyncio.sleep(2) # Allow for final JS rendering
            
            elements = driver.find_elements(By.CSS_SELECTOR, config["item_selector"])
            results = [el.text.strip() for el in elements[:max_items] if el.text.strip()]
            logger.info(f"-> Found {len(results)} items from {site_key}.")
        except Exception as e:
            logger.error(f"-> Failed to scrape {site_key}. Error: {e}")
        
        return { "source": site_key, "results": results }

    async def run_scraping_tasks(self, interest: str) -> List[Dict]:
        """Initializes a single browser and runs scrapers for all enabled sites."""
        driver = self._get_driver()
        tasks = []
        
        query = f'"{interest}" problem OR "how to"'

        for site_key, config in SITE_CONFIGS.items():
            if config["status"] == "enabled":
                tasks.append(self.scrape_site(driver, site_key, query))
            else:
                logger.warning(f"Skipping '{site_key}': {config['reason']}")

        try:
            scraped_data = await asyncio.gather(*tasks)
        finally:
            logger.info("All scraping tasks complete. Closing browser.")
            driver.quit()
        
        return [result for result in scraped_data if result.get('results')]


async def main(keyword: str):
    """
    Main orchestrator function.
    """
    logger.info(f"--- STARTING NICHESTACK AI UNIVERSAL SCRAPER ---")
    logger.info(f"Researching keyword: '{keyword}'")
    
    scraper = UniversalScraper()
    scraped_data = await scraper.run_scraping_tasks(keyword)
    
    final_report = {
        "keyword": keyword,
        "timestamp": datetime.now().isoformat(),
        "intelligence_report": scraped_data
    }
    
    logger.info("--- MARKET INTELLIGENCE REPORT ---")
    pprint(final_report)
    
    filename = f"intelligence_report_{keyword.replace(' ', '_')}.json"
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    logger.info(f"--- REPORT SAVED TO {filename} ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Market Research Scraper for NicheStack AI")
    parser.add_argument("keyword", type=str, help="The core keyword or niche to research.")
    args = parser.parse_args()
    
    # This ensures the async main function is run correctly
    asyncio.run(main(args.keyword))