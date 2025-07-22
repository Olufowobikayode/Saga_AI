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

# Initialize a logger for this module, our window into the process.
logger = logging.getLogger(__name__)

# --- Extractor Functions - Methods to distill wisdom from raw elements ---
def default_extractor(element: WebElement) -> str:
    """The default extractor, simply returns the element's text."""
    return element.text.strip() if element and hasattr(element, 'text') else ""

def get_href_extractor(element: WebElement) -> str:
    """An extractor for <a> tags, returns the link's text and its destination (URL)."""
    text = element.text.strip()
    href = element.get_attribute('href')
    return f"{text} ({href})" if text and href else ""

# --- SITE CONFIGURATION (The "Brain" of the Scraper) ---
# This is the grimoire from which Saga draws her knowledge of the web's structure.
# Each entry is a map to a stream of public consciousness.
# NOTE: For many of these sites, direct URL parameters for country or category
# filtering are not consistently available. The primary purpose of passing this context
# is for superior logging and for the AI to interpret the results within a defined scope.
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    # --- Community & Q&A Platforms (The Voice of the People) ---
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
    # --- Technical & Developer Platforms (The Voice of the Builders) ---
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
    # --- News & Current Events (The Pulse of the World) ---
    "Reuters": {
        "search_url_template": "https://www.reuters.com/site-search/?query={query}",
        "wait_selector": '[data-testid="Heading"]',
        "item_selector": '[data-testid="Heading"]',
        "query_type": "news",
        "extractor": default_extractor,
    },
    "BBC_News": {
        "search_url_template": "https://www.bbc.co.uk/search?q={query}",
        "wait_selector": 'main [aria-labelledby="search-content"] ul > li',
        "item_selector": 'main [aria-labelledby="search-content"] ul > li p',
        "query_type": "news",
        "extractor": default_extractor,
    },
    "The_Guardian": {
        "search_url_template": "https://www.theguardian.com/search?q={query}",
        "wait_selector": '[data-testid="results-list"] > li',
        "item_selector": '[data-testid="results-list"] > li .dcr-12qpde2 a',
        "query_type": "news",
        "extractor": default_extractor,
    },
    # --- General Knowledge & E-commerce ---
    "Medium": {
        "search_url_template": "https://medium.com/search?q={query}",
        "wait_selector": 'article',
        "item_selector": 'article h2',
        "query_type": "general",
        "extractor": default_extractor,
    },
    "Jumia": {
        "search_url_template": "https://www.jumia.com.ng/catalog/?q={query}",
        "wait_selector": 'article.prd',
        "item_selector": 'article.prd .name',
        "query_type": "product",
        "extractor": default_extractor,
    },
}

# --- QUERIES DICTIONARY (The Questions We Ask the Oracle) ---
QUERIES = {
    "pain_point": '"{interest}" problem OR "how to" OR "I need help with" OR "issues with {interest}"',
    "technical": '"{interest}" error OR "bug" OR "tutorial" OR "integration issue"',
    "general": '"{interest}" analysis OR "impact of {interest}"',
    "product": '"{interest}" reviews OR "best {interest}"',
    "news": '"{interest}"',
}

class SagaInsightScraper:
    """
    A robust, config-driven web scraper that acts as Saga's eyes upon the world.
    It uses Selenium to perceive modern, JavaScript-heavy websites, ensuring that
    no story, problem, or idea is hidden from view.
    """
    def _get_driver(self) -> webdriver.Chrome:
        """
        Summons a Chrome browser instance, configured for silent, efficient operation
        in any environment, from a local machine to the halls of a cloud server.
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            logger.error(f"Failed to initialize Chrome driver: {e}. The digital realm resists our gaze. Ensure Chrome and ChromeDriver are compatible and installed.")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during driver initialization: {e}")
            raise

    async def scrape_site(self, driver: webdriver.Chrome, site_key: str, query: str, max_items: int = 5,
                          country_code: Optional[str] = None, country_name: Optional[str] = None,
                          product_category: Optional[str] = None, product_subcategory: Optional[str] = None) -> Dict:
        """
        Gazes upon a single site using a shared browser instance, extracting its stories.

        Args:
            driver: A running Selenium WebDriver instance.
            site_key: The key to the site's entry in our SITE_CONFIGS grimoire.
            query: The question we are asking of the site.
            max_items: The maximum number of insights to glean.
            country_code: The 2-letter ISO code of the land we are observing.
            country_name: The full name of the land, for clarity in our logs.
            product_category: A more specific domain of inquiry.
            product_subcategory: A niche within that domain.

        Returns:
            A dictionary containing the site's name and a list of extracted insights.
        """
        config = SITE_CONFIGS[site_key]
        results = []
        
        # Build a detailed context string for our records, so we always remember the 'why' of our query.
        context_parts = []
        if country_name:
            context_parts.append(f"Country: {country_name}")
        if product_category:
            context_parts.append(f"Category: {product_category}")
        if product_subcategory:
            context_parts.append(f"Subcategory: {product_subcategory}")
        context_log_suffix = f" ({'; '.join(context_parts)})" if context_parts else ""

        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Peering into {site_key} for '{query}'{context_log_suffix}...")
            await asyncio.to_thread(driver.get, url)
            
            await asyncio.to_thread(WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"]))
            ))
            
            elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["item_selector"])
            extractor_func: Callable[[WebElement], str] = config.get("extractor", default_extractor)
            
            for el in elements[:max_items]:
                extracted_text = await asyncio.to_thread(extractor_func, el)
                if extracted_text:
                    results.append(extracted_text)
            
            if not results:
                logger.warning(f"Successfully connected to {site_key}, but found no matching items for selector '{config['item_selector']}'. The stream is quiet here.")
            else:
                logger.info(f"Gleaned {len(results)} insights from {site_key}{context_log_suffix}.")

        except TimeoutException:
            logger.warning(f"TimeoutException: The spirits of {site_key} are slow to answer{context_log_suffix}. The elements '{config['wait_selector']}' did not appear in time.")
        except NoSuchElementException:
            logger.warning(f"NoSuchElementException: The paths on {site_key} have changed{context_log_suffix}. Could not find elements with selector: '{config['item_selector']}'.")
        except Exception as e:
            logger.error(f"An unforeseen obstacle arose while scraping {site_key}{context_log_suffix}. Error: {e}", exc_info=True)
        
        return {"site": site_key, "query_type": config.get("query_type"), "results": [res for res in results if res]}

    async def scrape_multiple_sites(self, interest: str, sites: List[str],
                                   country_code: Optional[str] = None, country_name: Optional[str] = None,
                                   product_category: Optional[str] = None, product_subcategory: Optional[str] = None) -> List[Dict]:
        """
        Dispatches a single browser instance to gaze upon multiple sites in parallel,
        sharing its vision to conserve vital energy.

        Args:
            interest: The central theme of our inquiry (e.g., "home fitness").
            sites: A list of site keys from SITE_CONFIGS to observe.
            (and other context parameters for localization and categorization)

        Returns:
            A list of dictionaries, each a chapter of insights from a single site.
        """
        driver = None
        scraped_data = []
        try:
            driver = self._get_driver()
            tasks = []

            for site_key in sites:
                if site_key in SITE_CONFIGS:
                    config = SITE_CONFIGS[site_key]
                    query_type = config.get("query_type", "general")
                    query = QUERIES[query_type].format(interest=interest)
                    
                    tasks.append(self.scrape_site(driver, site_key, query, 
                                                  max_items=5, # Standardize max items for multi-scrape
                                                  country_code=country_code, country_name=country_name,
                                                  product_category=product_category, product_subcategory=product_subcategory))
                else:
                    logger.warning(f"A map for the site '{site_key}' was not found in our grimoire. Skipping.")

            scraped_data = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.critical(f"A critical error occurred while preparing our vision: {e}", exc_info=True)
            if driver:
                await asyncio.to_thread(driver.quit)
            return []
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)
                logger.info("The browser has been dismissed. Our vision ends.")
        
        successful_results = [
            result for result in scraped_data 
            if not isinstance(result, Exception) and result.get('results')
        ]
        
        return successful_results