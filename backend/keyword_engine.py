# file: backend/keyword_engine.py

import asyncio
import logging
from typing import List, Dict, Any
from urllib.parse import quote_plus
import os
import aiohttp # Asynchronous HTTP client for API calls

from pytrends.request import TrendReq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait # Corrected: Added import for WebDriverWait
from selenium.webdriver.support import expected_conditions as EC # Corrected: Added import for expected_conditions (EC)

logger = logging.getLogger(__name__)

# --- API KEY CONFIGURATION ---
# In a real enterprise app, these would be loaded securely (e.g., from os.environ)
# For now, we define them here. You would get these keys by subscribing to the services.
API_KEYS = {
    "KEYWORDTOOL_IO_API_KEY": os.environ.get("KEYWORDTOOL_IO_API_KEY"),
    # "UBERSUGGEST_API_KEY": os.environ.get("UBERSUGGEST_API_KEY"), # Example
}

class KeywordEngine:
    """
    An enterprise-grade, multi-source keyword intelligence engine.
    It follows an "API-First, Scrape-Second" philosophy, prioritizing reliable API
    integrations and falling back to intelligent scraping for public data.
    """

    def _get_driver(self) -> webdriver.Chrome:
        """Initializes a headless Chrome browser for scraping tasks."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    async def _run_in_executor(self, sync_func, *args, **kwargs) -> Any:
        """Runs a synchronous function in a separate thread."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: sync_func(*args, **kwargs))
    
    # --- Data Source Method: Google Trends (API) ---
    async def get_google_trends_data(self, interest: str) -> Dict:
        """Fetches related and rising queries from the pytrends library."""
        logger.info(f"Fetching Google Trends data for '{interest}'...")
        data = {"related": [], "rising": []}
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            await self._run_in_executor(pytrends.build_payload, kw_list=[interest], timeframe='today 3-m')
            related_queries = await self._run_in_executor(pytrends.related_queries)
            
            top = related_queries.get(interest, {}).get('top')
            rising = related_queries.get(interest, {}).get('rising')

            if top is not None and not top.empty:
                data["related"] = top['query'].tolist()[:5]
            if rising is not None and not rising.empty:
                data["rising"] = rising['query'].tolist()[:5]
        except Exception as e:
            logger.error(f"Pytrends API failed: {e}")
        return data

    # --- Data Source Method: KeywordTool.io (API) ---
    async def get_keywordtool_io_suggestions(self, interest: str) -> List[str]:
        """
        [API-FIRST] Fetches keyword suggestions from the official KeywordTool.io API.
        This is a placeholder and requires a valid API key.
        """
        api_key = API_KEYS.get("KEYWORDTOOL_IO_API_KEY")
        if not api_key:
            logger.warning("KeywordTool.io API key not found. Skipping.")
            return []
            
        logger.info(f"Fetching data from KeywordTool.io API for '{interest}'...")
        url = f"https://api.keywordtool.io/v2/search/suggestions/google?keyword={quote_plus(interest)}&country=US"
        headers = {"X-API-Key": api_key}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [item['string'] for item in data.get('results', {}).get('suggestions', [])[:10]]
                    else:
                        logger.error(f"KeywordTool.io API error: {response.status} - {await response.text()}")
        except Exception as e:
            logger.error(f"Failed to call KeywordTool.io API: {e}")
        return []

    # --- Data Source Method: AnswerThePublic (Scraping) ---
    async def scrape_answerthepublic_questions(self, interest: str) -> List[str]:
        """
        [SCRAPE-SECOND] Scrapes the "questions" section from AnswerThePublic.
        NOTE: This site is heavily protected and this scraper is fragile.
        """
        logger.info(f"Scraping AnswerThePublic for '{interest}'...")
        driver = self._get_driver()
        questions = []
        try:
            # The URL structure is simple
            driver.get(f"https://answerthepublic.com/{quote_plus(interest)}")
            # This site uses complex JS, so we wait for a specific data visualization element
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.search-vis-list__item'))
            )
            question_elements = driver.find_elements(By.CSS_SELECTOR, '.search-vis-list__item')
            questions = [el.text for el in question_elements[:10] if el.text]
        except Exception as e:
            logger.warning(f"Failed to scrape AnswerThePublic. This is common due to their anti-bot measures. Error: {e}")
        finally:
            driver.quit()
        return questions

    # --- Orchestrator Method ---
    async def get_full_keyword_strategy_data(self, interest: str) -> Dict:
        """
        The main public method for this engine. It orchestrates the gathering of
        data from all available sources in parallel.

        Args:
            interest: The user's core niche or keyword.

        Returns:
            A dictionary containing all the gathered keyword intelligence.
        """
        logger.info(f"Starting full keyword intelligence gathering for '{interest}'...")
        
        # Define all the data gathering tasks to run concurrently
        tasks = {
            "google_trends": self.get_google_trends_data(interest),
            "keywordtool_io": self.get_keywordtool_io_suggestions(interest),
            "answerthepublic": self.scrape_answerthepublic_questions(interest),
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        # Combine the results into a single, clean dictionary
        final_data = {}
        for task_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Task '{task_name}' failed with an exception: {result}")
                final_data[task_name] = {"error": str(result)}
            else:
                final_data[task_name] = result
        
        return final_data