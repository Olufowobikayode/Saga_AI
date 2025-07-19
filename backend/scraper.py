# file: backend/scraper.py

import asyncio
import logging
from urllib.parse import quote_plus
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize a logger for this module
logger = logging.getLogger(__name__)

# This is the "brain" of the scraper. It contains the specific instructions for each website.
# To add a new site from your list, you simply add a new entry to this dictionary.
# NOTE: Finding the correct selectors for each site is a manual process of using your
# browser's "Inspect Element" tool. The selectors below are examples and may change over time.
SITE_CONFIGS = {
    "Reddit": {
        "search_url_template": "https://www.reddit.com/search/?q={query}&type=comment",
        "wait_selector": '[data-testid="comment"]',
        "item_selector": '[data-testid="comment"] > div > div',
        "description": "Excellent for finding raw, unfiltered user pain points and opinions."
    },
    "Quora": {
        "search_url_template": "https://www.quora.com/search?q={query}",
        "wait_selector": '.qu-userText',
        "item_selector": '.qu-userText',
        "description": "Great for identifying the specific questions people are asking in a niche."
    },
    "StackOverflow": {
        "search_url_template": "https://stackoverflow.com/search?q={query}",
        "wait_selector": '.s-post-summary--content-title',
        "item_selector": '.s-post-summary--content .s-post-summary--content-title a',
        "description": "The best source for technical and programming-related problems."
    },
    "Medium": {
        "search_url_template": "https://medium.com/search?q={query}",
        "wait_selector": 'article h2',
        "item_selector": 'article h2',
        "description": "Useful for finding well-articulated thoughts and existing content on a topic."
    },
    "Bodybuilding.com": {
        "search_url_template": "https://forum.bodybuilding.com/search.php?s=&q={query}&search_type=post",
        "wait_selector": ".search-result-title",
        "item_selector": ".search-result-text",
        "description": "Example of a highly specific niche forum for fitness."
    },
    # To add more sites from your list (e.g., TripAdvisor), you would add a new entry here:
    # "TripAdvisor": {
    #     "search_url_template": "https://www.tripadvisor.com/Search?q={query}",
    #     "wait_selector": "[data-test-target='search-result']",  # This is a guess, you'd need to find the real one
    #     "item_selector": "a.result-title",                      # This is a guess
    #     "description": "Best for travel-related niches and finding user reviews."
    # },
}


class WebScraper:
    """
    A robust, config-driven web scraper using Selenium to handle modern, JavaScript-heavy websites.
    """
    def _get_driver(self):
        """Initializes a headless Google Chrome browser instance for scraping."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # This automatically downloads and manages the correct driver for Chrome
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    async def scrape_site(self, site_key: str, query: str, max_items: int = 3) -> Dict:
        """
        A generic scraper that uses the SITE_CONFIGS dictionary to scrape a specific site.
        It launches a browser, navigates to the search URL, waits for content to load,
        and extracts the text from the specified elements.

        Args:
            site_key: The key corresponding to a site in SITE_CONFIGS (e.g., "Reddit").
            query: The search term or phrase.
            max_items: The maximum number of text snippets to extract.

        Returns:
            A dictionary containing the site name and a list of extracted text results.
        """
        if site_key not in SITE_CONFIGS:
            logger.warning(f"No configuration found for site: {site_key}")
            return {"site": site_key, "results": []}

        config = SITE_CONFIGS[site_key]
        driver = self._get_driver()
        results = []
        
        try:
            # URL-encode the query to handle special characters safely
            url = config["search_url_template"].format(query=quote_plus(query))
            logger.info(f"Scraping {site_key} at URL: {url}")
            driver.get(url)
            
            # Wait for the primary content container to load to ensure JS has rendered
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["wait_selector"]))
            )
            
            # Find all the specified item elements on the page
            elements = driver.find_elements(By.CSS_SELECTOR, config["item_selector"])
            
            # Extract the text content from each element, ignoring empty ones
            results = [el.text for el in elements[:max_items] if el.text]
            logger.info(f"Successfully found {len(results)} items from {site_key}.")
            
        except Exception as e:
            logger.error(f"Failed to scrape {site_key}. URL: {driver.current_url}. Error: {e}")
            # In case of error, you might want to save the page source for debugging
            # with open(f"error_{site_key}.html", "w") as f:
            #     f.write(driver.page_source)
        finally:
            # Always ensure the browser instance is closed to free up resources
            driver.quit()
        
        return {"site": site_key, "results": results}

    async def scrape_multiple_sites(self, interest: str, sites: List[str]) -> List[Dict]:
        """
        Runs scrapers for a list of sites in parallel for maximum speed.
        This is the main entry point for the scraping service.

        Args:
            interest: The user's broad interest (e.g., "home fitness").
            sites: A list of site keys to scrape (e.g., ["Reddit", "Quora"]).

        Returns:
            A list of dictionaries, where each dictionary contains the results from one site.
        """
        # A more targeted query to find user problems
        query = f'"{interest}" problem OR "how to" OR "I need help with"'
        
        # Create a list of asynchronous tasks to run
        tasks = [self.scrape_site(site, query) for site in sites]
        
        # Run all scraping tasks concurrently and wait for them all to complete
        scraped_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out any tasks that resulted in an exception to ensure stable output
        successful_results = [
            result for result in scraped_data 
            if not isinstance(result, Exception) and result.get('results')
        ]
        
        return successful_results