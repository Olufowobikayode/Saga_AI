import asyncio
import logging
import json
from typing import List, Dict, Any, Callable, Optional
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SAGA:WISDOM] - %(message)s')
logger = logging.getLogger(__name__)


# --- THE MASTER SITE CONFIGURATION: Fortified for Resilience ---
# Saga's Insight: Selectors are now anchored to more stable attributes like 'data-testid'
# instead of volatile, style-based class names. This is the path to enduring knowledge.
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Reddit": {
        "status": "enabled",
        "search_url_template": "https://www.reddit.com/search/?q={query}&type=comment",
        # RESILIENT: 'data-testid' is used for testing and is less likely to change than styling classes.
        "wait_selector": '[data-testid="comment"]',
        "item_selector": '[data-testid="comment"] > div > div',
        "reason": "Provides raw, unfiltered user commentary and pain points."
    },
    "Quora": {
        "status": "enabled",
        "search_url_template": "https://www.quora.com/search?q={query}",
        # NOTE: Quora's classes are obfuscated and change. '.qu-userText' is the most stable available.
        "wait_selector": '.qu-userText',
        "item_selector": '.qu-userText',
        "reason": "A primary source for user questions and detailed problem explanations."
    },
    "Stack Exchange": {
        "status": "enabled",
        "search_url_template": "https://stackexchange.com/search?q={query}",
        # STABLE: This structure is core to Stack Exchange's post layout.
        "wait_selector": '.s-post-summary--content-title',
        "item_selector": '.s-post-summary--content-title .s-link',
        "reason": "High-quality, moderated Q&A across a wide range of professional topics."
    },
    "Medium": {
        "status": "enabled",
        "search_url_template": "https://medium.com/search?q={query}",
        # STABLE: 'article' and 'h2' are fundamental HTML tags, less prone to change than divs with classes.
        "wait_selector": 'article h2',
        "item_selector": 'article h2',
        "reason": "Captures expert opinions, tutorials, and thought leadership on the niche."
    },
    "GitHub Issues": {
        "status": "enabled",
        "search_url_template": "https://github.com/search?q={query}&type=issues",
        # STABLE: Core structure for issue lists.
        "wait_selector": '.issue-list-item',
        "item_selector": '.issue-list-item .markdown-title a',
        "reason": "Direct insight into technical problems, bugs, and feature requests."
    },
    "Dev.to": {
        "status": "enabled",
        "search_url_template": "https://dev.to/search?q={query}",
        # STABLE: Semantic and structural selectors.
        "wait_selector": 'article',
        "item_selector": 'h2.crayons-story__title a',
        "reason": "Community-driven technical articles and discussions."
    },
    # --- Deprecated or Protected Sites ---
    # Saga's Decree: We shall not waste our energy on fruitless endeavors against heavily fortified gates.
    # These are documented, but disabled, to focus our strength where it yields the most wisdom.
    "Answers.com": {"status": "protected", "reason": "Heavy JS, CAPTCHA protection makes scraping unreliable."},
    "Ask.fm": {"status": "protected", "reason": "Login-centric, not ideal for broad, unauthenticated scraping."},
    "Brainly": {"status": "protected", "reason": "Requires login and has strong anti-bot measures."},
    "Chegg": {"status": "requires_login", "reason": "All valuable content is behind a paywall."},
    "ResearchGate": {"status": "requires_login", "reason": "Academic network requiring login."},
}


class CommunitySaga:
    """
    I am Saga, the Seer of Community Whispers. I listen to the digital halls
    of Reddit, Quora, and other forums to gather the true voice of the people—their
    questions, their problems, their needs. My design is now more resilient, my
    sight more keen.
    """

    def _get_driver(self) -> webdriver.Chrome:
        """Configures and summons a Chrome spirit for our quest (a browser instance)."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            logger.error(f"The Chrome spirit could not be summoned. Ensure its path is known and its form is compatible. Error: {e}")
            raise

    async def _gather_from_site(self, driver: webdriver.Chrome, site_key: str, query: str,
                                country_code: Optional[str] = None, country_name: Optional[str] = None,
                                max_items: int = 5) -> Dict:
        """Gathers whispers from a single digital domain."""
        config = SITE_CONFIGS[site_key]
        results = []

        country_log_suffix = f" (Realm: {country_name or 'Global'})"
        url = config["search_url_template"].format(query=quote_plus(query))
        logger.info(f"Casting my sight upon {site_key} for '{query}'{country_log_suffix}...")

        try:
            await asyncio.to_thread(driver.get, url)

            await asyncio.to_thread(WebDriverWait(driver, 15).until,
                                   EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"])))

            await asyncio.sleep(2) # A moment of pause, for all echoes to settle.

            elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["item_selector"])

            for el in elements[:max_items]:
                text = await asyncio.to_thread(lambda: el.text.strip())
                if text:
                    results.append(text)

            logger.info(f"-> From {site_key}, I have gathered {len(results)} distinct whispers.")
        except TimeoutException:
            logger.warning(f"-> The currents of {site_key} were too slow or obscured my sight (Timeout). The knowledge remains hidden.")
        except NoSuchElementException:
            logger.warning(f"-> The halls of {site_key} have shifted. The patterns I sought were not found (NoSuchElement).")
        except Exception as e:
            logger.error(f"-> A powerful ward protects {site_key}, or the connection has failed. Error: {e}")

        return { "source": site_key, "results": [res for res in results if res] }

    async def run_community_gathering(self, interest: str,
                                       country_code: Optional[str] = None,
                                       country_name: Optional[str] = None) -> List[Dict]:
        """I orchestrate the grand gathering of voices from all enabled realms."""
        driver = None
        gathered_data = []
        try:
            driver = self._get_driver()
            tasks = []

            # A query forged to find true problems and needs
            query = f'"{interest}" problem OR "how to" OR "I need help with" OR "{interest}" issues'

            logger.info(f"I now seek the collective voice concerning '{interest}'...")
            for site_key, config in SITE_CONFIGS.items():
                if config["status"] == "enabled":
                    tasks.append(self._gather_from_site(driver, site_key, query, country_code, country_name))
                else:
                    logger.warning(f"I will not gaze upon '{site_key}'. Reason: {config['reason']}")

            gathered_data = await asyncio.gather(*tasks, return_exceptions=True)
            # Filter out failures and empty results, for only true wisdom should be presented.
            gathered_data = [res for res in gathered_data if not isinstance(res, Exception) and res.get('results')]

        except Exception as e:
            logger.critical(f"A great disturbance has disrupted the entire gathering. My sight is clouded. Error: {e}")
            if driver:
                await asyncio.to_thread(driver.quit)
            return []
        finally:
            if driver:
                logger.info("The gathering is complete. The Chrome spirit is dismissed.")
                await asyncio.to_thread(driver.quit)

        return gathered_data


async def main(keyword: str):
    """A standalone ritual to test my powers."""
    logger.info(f"--- SAGA'S INSIGHT ENGINE: COMMUNITY GATHERING ---")
    logger.info(f"Divining wisdom for keyword: '{keyword}'")

    saga_seer = CommunitySaga()
    sample_country_code = "US"
    sample_country_name = "United States"
    scraped_data = await saga_seer.run_community_gathering(keyword, sample_country_code, sample_country_name)

    final_report = {
        "divined_for": keyword,
        "realm_code": sample_country_code,
        "realm_name": sample_country_name,
        "timestamp_of_vision": datetime.now().isoformat(),
        "community_whispers": scraped_data
    }

    logger.info("--- SCROLL OF COMMUNITY WISDOM ---")
    pprint(final_report)

    filename = f"scroll_of_whispers_{keyword.replace(' ', '_')}_{sample_country_code}.json"
    try:
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        logger.info(f"--- The scroll has been inscribed and saved to {filename} ---")
    except IOError as e:
        logger.error(f"Failed to inscribe the scroll ({filename}): {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CommunitySaga: A Tool to Gather the Voice of the People")
    parser.add_argument("keyword", type=str, help="The core subject of divination.")
    args = parser.parse_args()

    asyncio.run(main(args.keyword))