--- START OF FILE backend/scraper.py ---
import asyncio
import logging
from urllib.parse import quote_plus
from typing import List, Dict, Any, Callable, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Initialize a logger for this module, reflecting its new purpose
logger = logging.getLogger(__name__)

# --- Extractor Functions (The Runes of Extraction) ---
def default_extractor(element: WebElement) -> str:
    """The default rune, simply returns the element's core text."""
    return element.text

def get_href_extractor(element: WebElement) -> str:
    """A rune for anchor tags, returning the link's text and its destination (URL)."""
    text = element.text
    href = element.get_attribute('href')
    return f"{text} ({href})" if text and href else ""

# --- SITE CONFIGURATION (Saga's Grimoire of Digital Realms) ---
# Saga's Insight: I have expanded our gaze to include the grand chronicles of the mortal world—
# the major news outlets. This provides a new dimension of wisdom: public sentiment and current events.
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    # --- Community Realms (The Voice of the People) ---
    "Reddit": {
        "search_url_template": "https://www.reddit.com/search/?q={query}&type=comment",
        "wait_selector": '[data-testid="comment"]',
        "item_selector": '[data-testid="comment"] > div > div',
        "query_type": "pain_point",
        "extractor": default_extractor,
    },
    "Quora": {
        "search_url_template": "https://www.quora.com/search?q={query}",
        "wait_selector": '.qu-userText',
        "item_selector": '.qu-userText',
        "query_type": "pain_point",
        "extractor": default_extractor,
    },
    # --- Technical Realms (The Halls of the Builders) ---
    "StackOverflow": {
        "search_url_template": "https://stackoverflow.com/search?q={query}",
        "wait_selector": '#mainbar',
        "item_selector": '.s-post-summary--content .s-post-summary--content-title a',
        "query_type": "technical",
        "extractor": default_extractor,
    },
    "GitHub": {
        "search_url_template": "https://github.com/search?q={query}&type=issues",
        "wait_selector": '.issue-list-item',
        "item_selector": '.issue-list-item .markdown-title a',
        "query_type": "technical",
        "extractor": default_extractor,
    },
    # --- News Realms (The Chronicles of Now) ---
    "BBC News": {
        "search_url_template": "https://www.bbc.co.uk/search?q={query}",
        "wait_selector": 'ul[role="list"] li',
        "item_selector": 'a[data-testid="internal-link"]',
        "query_type": "general",
        "extractor": default_extractor,
    },
    "Reuters": {
        "search_url_template": "https://www.reuters.com/site-search/?query={query}",
        "wait_selector": '[data-testid="search-results-list"]',
        "item_selector": 'a[data-testid="Heading"]',
        "query_type": "general",
        "extractor": default_extractor,
    },
    "The Guardian": {
        "search_url_template": "https://www.theguardian.com/search?q={query}",
        "wait_selector": '[data-testid="results-list"]',
        "item_selector": '.dcr-c06wz9 a', # Note: This class is auto-generated and highly fragile.
        "query_type": "general",
        "extractor": default_extractor,
    },
    "The New York Times": {
        "search_url_template": "https://www.nytimes.com/search?query={query}",
        "wait_selector": '[data-testid="search-results"]',
        "item_selector": 'h4.css-2fgx4k', # Note: This class is auto-generated and highly fragile.
        "query_type": "general",
        "extractor": default_extractor,
    },
    # --- Miscellaneous Realms ---
    "Medium": {
        "search_url_template": "https://medium.com/search?q={query}",
        "wait_selector": 'article',
        "item_selector": 'article h2',
        "query_type": "general",
        "extractor": default_extractor,
    },
}

# --- QUERIES DICTIONARY (The Words of Power) ---
QUERIES = {
    "pain_point": '"{interest}" problem OR "how to" OR "I need help with"',
    "technical": '"{interest}" error OR "bug" OR "tutorial"',
    "general": '"{interest}"',
    "product": '"{interest}"', # Kept for potential future use
}

class SagaWebOracle:
    """
    I am the SagaWebOracle. My sight pierces the digital veil, gathering truths
    from many realms—from the clamor of communities to the structured halls of
    builders, and now, to the ever-flowing river of world news.
    """
    def _get_driver(self) -> webdriver.Chrome:
        """Summons a Chrome spirit, optimized for its journey."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            logger.error(f"The Chrome spirit resists summoning. Ensure its essence is pure and its path is clear. Error: {e}")
            raise
        except Exception as e:
            logger.error(f"An unknown enchantment disrupted the summoning ritual. Error: {e}")
            raise


    async def _divine_from_site(self, driver: webdriver.Chrome, site_key: str, query: str, max_items: int = 3,
                                country_code: Optional[str] = None, country_name: Optional[str] = None,
                                product_category: Optional[str] = None, product_subcategory: Optional[str] = None) -> Dict:
        """Casts my vision upon a single digital realm to divine its secrets."""
        config = SITE_CONFIGS[site_key]
        results = []

        # Weave a suffix for our logs, rich with context.
        context_suffix_parts = []
        if country_name:
            context_suffix_parts.append(f"Realm: {country_name}")
        if product_category:
            context_suffix_parts.append(f"Domain: {product_category}")
        context_suffix = f" ({', '.join(context_suffix_parts)})" if context_suffix_parts else ""

        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Gazing into {site_key} for '{query}'{context_suffix}")
            await asyncio.to_thread(driver.get, url)

            await asyncio.to_thread(WebDriverWait(driver, 15).until,
                                   EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"])))

            elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["item_selector"])
            extractor_func: Callable[[WebElement], str] = config.get("extractor", default_extractor)

            for el in elements[:max_items]:
                extracted_text = await asyncio.to_thread(extractor_func, el)
                if extracted_text:
                    results.append(extracted_text)

            logger.info(f"-> My vision in {site_key} reveals {len(results)} truths.")
        except TimeoutException:
            logger.warning(f"The mists of {site_key} are too thick; my sight is obscured (Timeout).")
        except NoSuchElementException:
            logger.warning(f"The landscape of {site_key} has changed; the landmarks I seek are gone (NoSuchElement).")
        except Exception as e:
            logger.error(f"A powerful ward deflects my gaze from {site_key}. Error: {e}")

        return {"site": site_key, "results": [res for res in results if res]}

    async def divine_from_multiple_sites(self, interest: str, sites: List[str],
                                          country_code: Optional[str] = None, country_name: Optional[str] = None,
                                          product_category: Optional[str] = None, product_subcategory: Optional[str] = None) -> List[Dict]:
        """I send my consciousness across many realms at once, weaving their tales into a single saga."""
        driver = None
        gathered_data = []
        try:
            driver = self._get_driver()
            tasks = []

            for site_key in sites:
                if site_key in SITE_CONFIGS:
                    query_type = SITE_CONFIGS[site_key].get("query_type", "general")
                    query = QUERIES[query_type].format(interest=interest)
                    tasks.append(self._divine_from_site(driver, site_key, query,
                                                        country_code=country_code, country_name=country_name,
                                                        product_category=product_category, product_subcategory=product_subcategory))
                else:
                    logger.warning(f"The realm of '{site_key}' is not in my grimoire. I shall pass it by.")

            gathered_data = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.critical(f"A cataclysm has disrupted the grand divination! My connection to the digital ether is severed. Error: {e}")
            if driver:
                await asyncio.to_thread(driver.quit)
            return []
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)

        successful_results = [
            result for result in gathered_data
            if not isinstance(result, Exception) and result.get('results')
        ]

        return successful_results
--- END OF FILE backend/scraper.py ---