import asyncio
import logging
import json
from typing import List, Dict, Any, Callable, Optional
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SAGA:WISDOM] - %(message)s')
logger = logging.getLogger(__name__)


# --- THE MASTER SCROLL OF COMMUNITY & FORUM REALMS: Fortified and Expanded ---
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    # --- Community Realms (The Voice of the People) ---
    "Reddit": {
        "status": "enabled",
        "search_url_template": "https://www.reddit.com/search/?q={query}&type=comment",
        "wait_selector": '[data-testid="comment"]',
        "item_selector": '[data-testid="comment"] > div > div',
        "reason": "Provides raw, unfiltered commentary."
    },
    "Quora": {
        "status": "enabled",
        "search_url_template": "https://www.quora.com/search?q={query}",
        "wait_selector": '.qu-userText',
        "item_selector": '.qu-userText',
        "reason": "A primary forum for questions and explanations."
    },
    # --- Technical Realms (From the Halls of the Builders) ---
    "Stack Overflow": {
        "status": "enabled",
        "search_url_template": "https://stackoverflow.com/search?q={query}",
        "wait_selector": '#mainbar .s-post-summary',
        "item_selector": '.s-post-summary--content-title .s-link',
        "reason": "Offers high-quality technical Q&A."
    },
    "GitHub Issues": {
        "status": "enabled",
        "search_url_template": "https://github.com/search?q={query}&type=issues",
        "wait_selector": '.issue-list-item',
        "item_selector": '.issue-list-item .markdown-title a',
        "reason": "Direct insight into software problems and feature requests."
    },
    # --- Thought Leadership Realm ---
    "Medium": {
        "status": "enabled",
        "search_url_template": "https://medium.com/search?q={query}",
        "wait_selector": 'article h2',
        "item_selector": 'article h2',
        "reason": "Captures expert sagas and tutorials."
    },
    # --- Deprecated or Protected Realms ---
    "Answers.com": {"status": "protected", "reason": "Heavy JS wards and CAPTCHA runes."},
    "Ask.fm": {"status": "protected", "reason": "Login-centric; not for broad divination."},
    "Brainly": {"status": "protected", "reason": "Requires login and has strong anti-bot wards."},
}

# --- THE GRIMOIRE OF QUERIES ---
QUERY_GRIMOIRE: Dict[str, str] = {
    "pain_point": '"{interest}" problem OR "how to" OR "I need help with" OR "{interest}" issues',
    "questions": 'who OR what OR when OR where OR why OR how "{interest}"',
    "positive_feedback": '"{interest}" love OR "best" OR "favorite" OR "amazing"',
    "comparisons": '"{interest}" vs OR "or" OR "alternative to"',
    "technical_issues": '"{interest}" error OR "bug" OR "issue" OR "fix"',
}

class CommunitySaga:
    """
    I am the Seer of Community Whispers, an aspect of the great Saga. I journey
    through the digital halls of forums and communities to gather the true voice of
    the people—their questions, problems, and technical challenges.
    This Seer is now enhanced with stealth capabilities to appear more human.
    """

    def __init__(self):
        # ### ENHANCEMENT: Initialize the UserAgent object once.
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

    def _get_driver(self) -> webdriver.Chrome:
        """Configures and summons a stealthy Chrome spirit for our quest."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # ### ENHANCEMENT 1: Use a randomized, real-world user agent for each request.
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
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
            logger.error(f"The Chrome spirit could not be summoned. Error: {e}")
            raise

    async def _gather_from_realm(self, driver: webdriver.Chrome, site_key: str, query: str, max_items: int = 5) -> Dict:
        """Gathers whispers from a single digital domain."""
        config = SITE_CONFIGS[site_key]
        results = []

        url = config["search_url_template"].format(query=quote_plus(query))
        logger.info(f"Casting my sight upon {site_key} for '{query}'...")

        try:
            await asyncio.to_thread(driver.get, url)
            await asyncio.to_thread(WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"]))))
            
            # ### ENHANCEMENT 3: Use randomized delays to better mimic human behavior.
            await asyncio.sleep(random.uniform(2.1, 3.9))
            
            elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["item_selector"])

            for el in elements[:max_items]:
                text = await asyncio.to_thread(lambda: el.text.strip())
                if text:
                    results.append(text)

            logger.info(f"-> From the realm of {site_key}, I have gathered {len(results)} distinct whispers.")
        except TimeoutException:
            logger.warning(f"-> The mists of {site_key} were too slow or obscured my sight (Timeout).")
        except NoSuchElementException:
            logger.warning(f"-> The halls of {site_key} have shifted. The patterns I sought were not found.")
        except Exception as e:
            logger.error(f"-> A powerful ward protects {site_key}, or the connection has failed. Error: {e}")

        return { "source": site_key, "results": [res for res in results if res] }

    async def run_community_gathering(self, 
                                       interest: str,
                                       query_type: str = "pain_point",
                                       sites_to_scan: Optional[List[str]] = None) -> List[Dict]:
        """
        I orchestrate the grand gathering of voices from specified community realms.
        If no sites are specified, I will consult all enabled realms.
        """
        driver = None
        gathered_data = []
        
        realms_to_visit = sites_to_scan if sites_to_scan else [key for key, config in SITE_CONFIGS.items() if config['status'] == 'enabled']

        try:
            driver = self._get_driver()
            
            query_template = QUERY_GRIMOIRE.get(query_type, QUERY_GRIMOIRE["pain_point"])
            query = query_template.format(interest=interest)

            logger.info(f"I now seek the collective voice concerning '{interest}' (Query Type: {query_type}) across {len(realms_to_visit)} realms...")
            
            tasks = []
            for site_key in realms_to_visit:
                if site_key in SITE_CONFIGS and SITE_CONFIGS[site_key]["status"] == "enabled":
                    tasks.append(self._gather_from_realm(driver, site_key, query))
                else:
                    logger.warning(f"I will not gaze upon the realm of '{site_key}', as it is not in my enabled scrolls.")

            gathered_data = await asyncio.gather(*tasks, return_exceptions=True)
            gathered_data = [res for res in gathered_data if not isinstance(res, Exception) and res.get('results')]

        except Exception as e:
            logger.critical(f"A great disturbance has disrupted the gathering of whispers. My sight is clouded. Error: {e}")
            return [] # Return empty list on critical failure
        finally:
            if driver:
                logger.info("The gathering of whispers is complete. The Chrome spirit is dismissed.")
                await asyncio.to_thread(driver.quit)

        return gathered_data


async def main(keyword: str, query_type: str):
    """A standalone ritual to test my powers of community divination."""
    logger.info(f"--- SAGA'S INSIGHT ENGINE: GATHERING OF WHISPERS ---")
    logger.info(f"Divining wisdom for keyword: '{keyword}' using query type: '{query_type}'")

    saga_seer = CommunitySaga()
    
    scraped_data = await saga_seer.run_community_gathering(keyword, query_type=query_type)

    final_report = {
        "divined_for": keyword,
        "query_type": query_type,
        "timestamp_of_vision": datetime.now().isoformat(),
        "community_whispers_gathered": scraped_data
    }

    logger.info("--- SCROLL OF COMMUNITY WISDOM ---")
    pprint(final_report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CommunitySaga: A Tool to Gather the Voice of the People")
    parser.add_argument("keyword", type=str, help="The core subject of divination.")
    parser.add_argument("--query_type", type=str, default="pain_point", choices=QUERY_GRIMOIRE.keys(),
                        help="The type of query to perform.")
    args = parser.parse_args()

    asyncio.run(main(args.keyword, args.query_type))