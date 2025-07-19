# file: backend/scraper.py

import asyncio
import logging
from urllib.parse import quote_plus
from typing import List, Dict, Any, Callable

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize a logger for this module
logger = logging.getLogger(__name__)

# --- Extractor Functions ---
# This allows for custom logic to get the text from different types of elements.
def default_extractor(element: WebElement) -> str:
    """The default extractor, simply returns the element's text."""
    return element.text

def get_href_extractor(element: WebElement) -> str:
    """An extractor for <a> tags, returns the link's text and URL."""
    text = element.text
    href = element.get_attribute('href')
    return f"{text} ({href})" if text and href else ""

# --- SITE CONFIGURATION (The "Brain" of the Scraper) ---
# This configuration is now more powerful and flexible.
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
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
    "StackOverflow": {
        "search_url_template": "https://stackoverflow.com/search?q={query}",
        "wait_selector": '#mainbar',
        "item_selector": '.s-post-summary--content .s-post-summary--content-title a',
        "query_type": "technical",
        "extractor": default_extractor,
    },
    "Medium": {
        "search_url_template": "https://medium.com/search?q={query}",
        "wait_selector": 'article',
        "item_selector": 'article h2',
        "query_type": "general",
        "extractor": default_extractor,
    },
    "GitHub": {
        "search_url_template": "https://github.com/search?q={query}&type=issues",
        "wait_selector": '.issue-list-item',
        "item_selector": '.issue-list-item .markdown-title a',
        "query_type": "technical",
        "extractor": default_extractor,
    },
    # --- Example of an E-commerce Scraper (for a future stack) ---
    "Jumia": {
        "search_url_template": "https://www.jumia.com.ng/catalog/?q={query}",
        "wait_selector": 'article.prd',
        "item_selector": 'article.prd .name', # Simplified, would need price too
        "query_type": "product",
        "extractor": default_extractor,
    },
    # You can easily add more of the 80+ sites here by defining their selectors and query type.
}

# --- QUERIES DICTIONARY ---
# This separates the "what to search for" from the "how to scrape".
QUERIES = {
    "pain_point": '"{interest}" problem OR "how to" OR "I need help with"',
    "technical": '"{interest}" error OR "bug" OR "tutorial"',
    "general": '"{interest}"',
    "product": '"{interest}"',
}

class WebScraper:
    """
    A robust, config-driven web scraper using Selenium to handle modern, 
    JavaScript-heavy websites. It is designed to be efficient and resilient.
    """
    def _get_driver(self) -> webdriver.Chrome:
        """
        Initializes and returns a headless Google Chrome browser instance for scraping.
        This includes optimized options for running in a containerized environment like Render.
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    async def scrape_site(self, driver: webdriver.Chrome, site_key: str, query: str, max_items: int = 3) -> Dict:
        """
        Scrapes a single site using a shared, pre-initialized browser instance.

        Args:
            driver: A running Selenium WebDriver instance.
            site_key: The key corresponding to a site in SITE_CONFIGS.
            query: The search term or phrase.
            max_items: The maximum number of text snippets to extract.

        Returns:
            A dictionary containing the site name and a list of extracted text results.
        """
        config = SITE_CONFIGS[site_key]
        results = []
        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Navigating to {site_key} at URL: {url}")
            driver.get(url)
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"]))
            )
            
            elements = driver.find_elements(By.CSS_SELECTOR, config["item_selector"])
            extractor_func: Callable[[WebElement], str] = config.get("extractor", default_extractor)
            
            results = [extractor_func(el) for el in elements[:max_items] if el]
            logger.info(f"Successfully found {len(results)} items from {site_key}.")
        except Exception as e:
            logger.error(f"Failed to scrape {site_key}. URL: {driver.current_url}. Error: {e}")
        
        return {"site": site_key, "results": [res for res in results if res]} # Filter out empty results

    async def scrape_multiple_sites(self, interest: str, sites: List[str]) -> List[Dict]:
        """
        Initializes a single browser instance and runs scrapers for a list of sites 
        in parallel, sharing the browser to conserve resources.

        Args:
            interest: The user's broad interest (e.g., "home fitness").
            sites: A list of site keys from SITE_CONFIGS to scrape.

        Returns:
            A list of dictionaries, where each contains the results from one site.
        """
        driver = self._get_driver()
        tasks = []

        for site_key in sites:
            if site_key in SITE_CONFIGS:
                query_type = SITE_CONFIGS[site_key].get("query_type", "general")
                query = QUERIES[query_type].format(interest=interest)
                tasks.append(self.scrape_site(driver, site_key, query))
            else:
                logger.warning(f"No configuration found for site: {site_key}. Skipping.")

        try:
            scraped_data = await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            # Crucially, we always close the driver after all tasks are done.
            driver.quit()
        
        successful_results = [
            result for result in scraped_data 
            if not isinstance(result, Exception) and result.get('results')
        ]
        
        return successful_results