--- START OF FILE backend/scraper.py ---
import asyncio
import logging
from urllib.parse import quote_plus
from typing import List, Dict, Any, Callable, Optional # Added Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Initialize a logger for this module
logger = logging.getLogger(__name__)

# --- Extractor Functions ---
def default_extractor(element: WebElement) -> str:
    """The default extractor, simply returns the element's text."""
    return element.text

def get_href_extractor(element: WebElement) -> str:
    """An extractor for <a> tags, returns the link's text and URL."""
    text = element.text
    href = element.get_attribute('href')
    return f"{text} ({href})" if text and href else ""

# --- SITE CONFIGURATION (The "Brain" of the Scraper) ---
# NOTE: For many of these sites (especially Q&A/community forums), direct URL parameters
# for country or category filtering are not consistently available or effective.
# The primary purpose of passing country/category here is for contextual logging and
# for the AI to interpret the results within that defined scope.
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
    # Jumia is an e-commerce example that *could* be extended for category/subcategory search params
    # but that complexity would be in its specific 'scraper' implementation here if needed,
    # or rely on the global_ecommerce_scraper for more dedicated product search.
    "Jumia": {
        "search_url_template": "https://www.jumia.com.ng/catalog/?q={query}",
        "wait_selector": 'article.prd',
        "item_selector": 'article.prd .name',
        "query_type": "product",
        "extractor": default_extractor,
    },
}

# --- QUERIES DICTIONARY ---
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
        
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            logger.error(f"Failed to initialize Chrome driver: {e}. Ensure Chrome and ChromeDriver are compatible and installed.")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during driver initialization: {e}")
            raise


    async def scrape_site(self, driver: webdriver.Chrome, site_key: str, query: str, max_items: int = 3,
                          country_code: Optional[str] = None, country_name: Optional[str] = None,
                          product_category: Optional[str] = None, product_subcategory: Optional[str] = None) -> Dict:
        """
        Scrapes a single site using a shared, pre-initialized browser instance.

        Args:
            driver: A running Selenium WebDriver instance.
            site_key: The key corresponding to a site in SITE_CONFIGS.
            query: The search term or phrase.
            max_items: The maximum number of text snippets to extract.
            country_code: 2-letter ISO country code for context.
            country_name: Full country name for context.
            product_category: Optional category for context.
            product_subcategory: Optional subcategory for context.

        Returns:
            A dictionary containing the site name and a list of extracted text results.
        """
        config = SITE_CONFIGS[site_key]
        results = []
        
        # Build contextual log suffix
        context_suffix = ""
        if country_name:
            context_suffix += f" (Country: {country_name}"
            if country_code:
                context_suffix += f" - {country_code}"
            context_suffix += ")"
        if product_category:
            context_suffix += f" [Category: {product_category}"
            if product_subcategory:
                context_suffix += f" / {product_subcategory}"
            context_suffix += "]"

        try:
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Navigating to {site_key} at URL: {url}{context_suffix}")
            await asyncio.to_thread(driver.get, url)
            
            await asyncio.to_thread(WebDriverWait(driver, 15).until,
                                   EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"])))
            
            elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["item_selector"])
            extractor_func: Callable[[WebElement], str] = config.get("extractor", default_extractor)
            
            for el in elements[:max_items]:
                extracted_text = await asyncio.to_thread(extractor_func, el)
                if extracted_text:
                    results.append(extracted_text)
            
            logger.info(f"Successfully found {len(results)} items from {site_key}{context_suffix}.")
        except TimeoutException:
            logger.warning(f"TimeoutException while scraping {site_key}{context_suffix}. Elements did not load within expected time. URL: {driver.current_url}")
        except NoSuchElementException:
            logger.warning(f"NoSuchElementException while scraping {site_key}{context_suffix}. Expected elements not found. Selector: {config['item_selector']}. URL: {driver.current_url}")
        except Exception as e:
            logger.error(f"Failed to scrape {site_key}{context_suffix}. URL: {driver.current_url}. Error: {e}")
        
        return {"site": site_key, "results": [res for res in results if res]}

    async def scrape_multiple_sites(self, interest: str, sites: List[str],
                                   country_code: Optional[str] = None, country_name: Optional[str] = None,
                                   product_category: Optional[str] = None, product_subcategory: Optional[str] = None) -> List[Dict]:
        """
        Initializes a single browser instance and runs scrapers for a list of sites 
        in parallel, sharing the browser to conserve resources.

        Args:
            interest: The user's broad interest (e.g., "home fitness").
            sites: A list of site keys from SITE_CONFIGS to scrape.
            country_code: 2-letter ISO country code for localization context.
            country_name: Full country name for localization context.
            product_category: Optional category for context.
            product_subcategory: Optional subcategory for context.

        Returns:
            A list of dictionaries, where each contains the results from one site.
        """
        driver = None
        scraped_data = []
        try:
            driver = self._get_driver()
            tasks = []

            for site_key in sites:
                if site_key in SITE_CONFIGS:
                    query_type = SITE_CONFIGS[site_key].get("query_type", "general")
                    query = QUERIES[query_type].format(interest=interest)
                    # Pass all context parameters down to scrape_site
                    tasks.append(self.scrape_site(driver, site_key, query, 
                                                  country_code, country_name,
                                                  product_category, product_subcategory))
                else:
                    logger.warning(f"No configuration found for site: {site_key}. Skipping.")

            scraped_data = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.critical(f"Critical error during multi-site scraping initialization or execution: {e}")
            if driver:
                await asyncio.to_thread(driver.quit)
            return []
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)
        
        successful_results = [
            result for result in scraped_data 
            if not isinstance(result, Exception) and result.get('results')
        ]
        
        return successful_results
--- END OF FILE backend/scraper.py ---