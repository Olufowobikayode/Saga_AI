--- START OF FILE backend/q_and_a.py ---
import asyncio
import logging
import json
from typing import List, Dict, Any, Callable, Optional # Added Optional
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


# --- THE MASTER SITE CONFIGURATION ---
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    # General Q&A and Community Platforms
    # These sites are generally global or rely on user browser settings for localization.
    # Direct country filtering via URL parameters for scraping is often not straightforward.
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
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            logger.error(f"Failed to initialize Chrome driver: {e}. Ensure Chrome and ChromeDriver are compatible and installed.")
            raise

    async def scrape_site(self, driver: webdriver.Chrome, site_key: str, query: str, 
                          country_code: Optional[str] = None, country_name: Optional[str] = None, # New parameters
                          max_items: int = 5) -> Dict:
        """Scrapes a single site using a shared, pre-initialized browser instance."""
        config = SITE_CONFIGS[site_key]
        results = []
        
        # Log country context for better debugging and understanding
        country_log_suffix = f" (Country: {country_name or 'Global'})"

        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Navigating to {site_key} at URL: {url}{country_log_suffix}...")
            await asyncio.to_thread(driver.get, url)
            
            await asyncio.to_thread(WebDriverWait(driver, 15).until,
                                   EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"])))
            
            await asyncio.sleep(2) # Allow for final JS rendering
            
            elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["item_selector"])
            
            for el in elements[:max_items]:
                text = await asyncio.to_thread(lambda: el.text.strip())
                if text:
                    results.append(text)
            
            logger.info(f"-> Found {len(results)} items from {site_key}{country_log_suffix}.")
        except TimeoutException:
            logger.warning(f"-> Timed out waiting for elements on {site_key}{country_log_suffix}. URL: {driver.current_url}")
        except NoSuchElementException:
            logger.warning(f"-> Expected elements not found on {site_key}{country_log_suffix}. Selector: {config['wait_selector']} or {config['item_selector']}. URL: {driver.current_url}")
        except Exception as e:
            logger.error(f"-> Failed to scrape {site_key}{country_log_suffix}. Error: {e}")
        
        return { "source": site_key, "results": [res for res in results if res] }

    async def run_scraping_tasks(self, interest: str, 
                                 country_code: Optional[str] = None, # New parameter
                                 country_name: Optional[str] = None) -> List[Dict]: # New parameter
        """Initializes a single browser and runs scrapers for all enabled sites."""
        driver = None
        scraped_data = []
        try:
            driver = self._get_driver()
            tasks = []
            
            query = f'"{interest}" problem OR "how to" OR "I need help with" OR "{interest}" issues'

            for site_key, config in SITE_CONFIGS.items():
                if config["status"] == "enabled":
                    # Pass country code and name to individual site scraper for logging/context
                    tasks.append(self.scrape_site(driver, site_key, query, country_code, country_name))
                else:
                    logger.warning(f"Skipping '{site_key}': {config['reason']}")

            scraped_data = await asyncio.gather(*tasks, return_exceptions=True)
            scraped_data = [res for res in scraped_data if not isinstance(res, Exception) and res.get('results')]

        except Exception as e:
            logger.critical(f"Failed to initialize or run universal scraper: {e}")
            if driver:
                await asyncio.to_thread(driver.quit)
            return []
        finally:
            if driver:
                logger.info("All scraping tasks complete. Closing browser.")
                await asyncio.to_thread(driver.quit)
        
        return scraped_data


async def main(keyword: str):
    """
    Main orchestrator function for standalone execution.
    """
    logger.info(f"--- STARTING NICHESTACK AI UNIVERSAL SCRAPER ---")
    logger.info(f"Researching keyword: '{keyword}'")
    
    scraper = UniversalScraper()
    # For standalone testing, provide sample country data
    sample_country_code = "US"
    sample_country_name = "United States"
    scraped_data = await scraper.run_scraping_tasks(keyword, sample_country_code, sample_country_name)
    
    final_report = {
        "keyword": keyword,
        "country_code": sample_country_code,
        "country_name": sample_country_name,
        "timestamp": datetime.now().isoformat(),
        "intelligence_report": scraped_data
    }
    
    logger.info("--- MARKET INTELLIGENCE REPORT ---")
    pprint(final_report)
    
    filename = f"intelligence_report_{keyword.replace(' ', '_')}_{sample_country_code}.json"
    try:
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        logger.info(f"--- REPORT SAVED TO {filename} ---")
    except IOError as e:
        logger.error(f"Failed to save report to file {filename}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Market Research Scraper for NicheStack AI")
    parser.add_argument("keyword", type=str, help="The core keyword or niche to research.")
    args = parser.parse_args()
    
    asyncio.run(main(args.keyword))
--- END OF FILE backend/q_and_a.py ---