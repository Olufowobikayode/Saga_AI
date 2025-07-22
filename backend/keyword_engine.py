--- START OF FILE backend/keyword_engine.py ---
import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import os
import aiohttp

from pytrends.request import TrendReq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

logger = logging.getLogger(__name__)

# --- API KEY CONFIGURATION ---
API_KEYS = {
    "KEYWORDTOOL_IO_API_KEY": os.environ.get("KEYWORDTOOL_IO_API_KEY"),
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
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            logger.error(f"Failed to initialize Chrome driver for KeywordEngine: {e}")
            raise

    async def _run_in_executor(self, sync_func, *args, **kwargs) -> Any:
        """Runs a synchronous function in a separate thread to prevent blocking the event loop."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: sync_func(*args, **kwargs))
    
    # --- Data Source Method: Google Trends (API) ---
    async def get_google_trends_data(self, interest: str, country_code: Optional[str] = None) -> Dict:
        """
        Fetches related and rising queries from Google Trends, localized by country code.
        """
        logger.info(f"Fetching Google Trends data for '{interest}' in country code '{country_code}'...")
        data = {"related": [], "rising": []}
        try:
            # hl is interface language, tz is timezone. geo is for the search region.
            pytrends = TrendReq(hl='en-US', tz=360) 
            
            # Pass geo parameter for country-specific trends
            geo_param = country_code.upper() if country_code else '' # Use uppercase for ISO code
            
            await self._run_in_executor(pytrends.build_payload, kw_list=[interest], timeframe='today 3-m', geo=geo_param)
            related_queries = await self._run_in_executor(pytrends.related_queries)
            
            top = related_queries.get(interest, {}).get('top')
            rising = related_queries.get(interest, {}).get('rising')

            if top is not None and not top.empty:
                data["related"] = top['query'].tolist()[:5]
            if rising is not None and not rising.empty:
                data["rising"] = rising['query'].tolist()[:5]
        except Exception as e:
            logger.error(f"Pytrends API failed for interest '{interest}' in country '{country_code}': {e}")
            data["error"] = str(e)
        return data

    # --- Data Source Method: KeywordTool.io (API) ---
    async def get_keywordtool_io_suggestions(self, interest: str, country_code: Optional[str] = None) -> List[str]:
        """
        [API-FIRST] Fetches keyword suggestions from the official KeywordTool.io API, localized by country code.
        Requires a valid API key.
        """
        api_key = API_KEYS.get("KEYWORDTOOL_IO_API_KEY")
        if not api_key:
            logger.warning("KeywordTool.io API key not found. Skipping KeywordTool.io suggestions.")
            return []
            
        logger.info(f"Fetching data from KeywordTool.io API for '{interest}' in country code '{country_code}'...")
        
        url_params = f"keyword={quote_plus(interest)}"
        if country_code:
            url_params += f"&country={country_code.upper()}" # KeywordTool.io typically uses 2-letter ISO codes
        
        url = f"https://api.keywordtool.io/v2/search/suggestions/google?{url_params}"
        headers = {"X-API-Key": api_key}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return [item['string'] for item in data.get('results', {}).get('suggestions', [])[:10]]
        except aiohttp.ClientError as e:
            logger.error(f"KeywordTool.io API request failed for '{interest}' in country '{country_code}': {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from KeywordTool.io API for '{interest}' in country '{country_code}': {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred calling KeywordTool.io API for '{interest}' in country '{country_code}': {e}")
        return []

    # --- Data Source Method: AnswerThePublic (Scraping) ---
    async def scrape_answerthepublic_questions(self, interest: str, country_code: Optional[str] = None, country_name: Optional[str] = None) -> List[str]:
        """
        [SCRAPE-SECOND] Scrapes the "questions" section from AnswerThePublic.
        NOTE: This site is heavily protected and this scraper is fragile.
        Localization is limited for this scraper directly, but country context can be logged.
        """
        logger.info(f"Scraping AnswerThePublic for '{interest}' (Country: {country_name or 'Global'})...")
        driver = None
        questions = []
        try:
            driver = self._get_driver()
            # AnswerThePublic's localization is not simply URL-based in a scrapeable way
            # It relies on browser settings or internal detection.
            # We'll stick to the base URL for now.
            await asyncio.to_thread(driver.get, f"https://answerthepublic.com/{quote_plus(interest)}")
            
            await asyncio.to_thread(WebDriverWait(driver, 20).until,
                                   EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.search-vis-list__item')))
            
            await asyncio.sleep(2)

            question_elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, '.search-vis-list__item')
            questions = [await asyncio.to_thread(lambda: el.text) for el in question_elements[:10] if await asyncio.to_thread(lambda: el.text)]
            logger.info(f"Found {len(questions)} questions from AnswerThePublic.")
        except TimeoutException:
            logger.warning(f"Timeout while scraping AnswerThePublic for '{interest}'. This is common.")
        except NoSuchElementException:
            logger.warning(f"Expected elements not found on AnswerThePublic for '{interest}'. Site structure may have changed.")
        except Exception as e:
            logger.warning(f"Failed to scrape AnswerThePublic for '{interest}'. Error: {e}")
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)
        return questions

    # --- Orchestrator Method ---
    async def get_full_keyword_strategy_data(self, 
                                            interest: str, 
                                            country_code: Optional[str] = None, 
                                            country_name: Optional[str] = None,
                                            product_category: Optional[str] = None,
                                            product_subcategory: Optional[str] = None) -> Dict:
        """
        The main public method for this engine. It orchestrates the gathering of
        data from all available sources in parallel, considering country context.

        Args:
            interest: The user's core niche or keyword.
            country_code: 2-letter ISO country code for localization.
            country_name: Full country name for logging/context.
            product_category: Optional category for refinement.
            product_subcategory: Optional subcategory for refinement.

        Returns:
            A dictionary containing all the gathered keyword intelligence.
        """
        logger.info(f"Starting full keyword intelligence gathering for '{interest}' in '{country_name or 'Global'}'...")
        
        tasks = {
            "google_trends": self.get_google_trends_data(interest, country_code),
            "keywordtool_io": self.get_keywordtool_io_suggestions(interest, country_code),
            "answerthepublic": self.scrape_answerthepublic_questions(interest, country_code, country_name),
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        final_data = {}
        for task_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Task '{task_name}' failed with an exception for '{interest}' in country '{country_code}': {result}")
                final_data[task_name] = {"error": str(result)}
            else:
                final_data[task_name] = result
        
        return final_data
--- END OF FILE backend/keyword_engine.py ---