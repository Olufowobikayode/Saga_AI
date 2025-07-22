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

class KeywordRuneKeeper:
    """
    A specialist aspect of Saga, the Keeper of Digital Runes. It consults the most
    structured oracles (APIs) to decipher the power and meaning of keywords.
    It follows Saga's primary decree: "Seek the inscribed rune (API) before reading the shifting sands (scraping)."
    """

    def _get_driver(self) -> webdriver.Chrome:
        """Summons a Chrome spirit, only when needed for reading the shifting sands."""
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
            logger.error(f"The Chrome spirit for the Rune Keeper could not be summoned: {e}")
            raise

    async def _run_in_executor(self, sync_func, *args, **kwargs) -> Any:
        """A rite to run synchronous incantations in a separate thread, so as not to block the flow of wisdom."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: sync_func(*args, **kwargs))
    
    async def divine_from_google_trends(self, interest: str, country_code: Optional[str] = None) -> Dict:
        """
        Divines the rising and related keyword runes from the great Google Trends oracle.
        """
        logger.info(f"Divining Google Trends runes for '{interest}' in realm '{country_code}'...")
        data = {"related": [], "rising": []}
        try:
            pytrends = TrendReq(hl='en-US', tz=360) 
            geo_param = country_code.upper() if country_code else ''
            
            await self._run_in_executor(pytrends.build_payload, kw_list=[interest], timeframe='today 3-m', geo=geo_param)
            related_queries = await self._run_in_executor(pytrends.related_queries)
            
            top = related_queries.get(interest, {}).get('top')
            rising = related_queries.get(interest, {}).get('rising')

            if top is not None and not top.empty:
                data["related"] = top['query'].tolist()[:5]
            if rising is not None and not rising.empty:
                data["rising"] = rising['query'].tolist()[:5]
        except Exception as e:
            logger.error(f"The Google Trends oracle was silent for '{interest}' in realm '{country_code}': {e}")
            data["error"] = str(e)
        return data

    async def decipher_from_keywordtool_io(self, interest: str, country_code: Optional[str] = None) -> List[str]:
        """
        [RUNE-FIRST] Deciphers keyword suggestions from the sacred KeywordTool.io API scrolls.
        Requires a key to the library (API Key).
        """
        api_key = API_KEYS.get("KEYWORDTOOL_IO_API_KEY")
        if not api_key:
            logger.warning("The key to the KeywordTool.io library is missing. I cannot read its scrolls.")
            return []
            
        logger.info(f"Unsealing the KeywordTool.io scrolls for '{interest}' in realm '{country_code}'...")
        
        url = f"https://api.keywordtool.io/v2/search/suggestions/google?keyword={quote_plus(interest)}"
        if country_code:
            url += f"&country={country_code.upper()}"
        headers = {"X-API-Key": api_key}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return [item['string'] for item in data.get('results', {}).get('suggestions', [])[:10]]
        except Exception as e:
            logger.error(f"Failed to decipher the scrolls of KeywordTool.io for '{interest}': {e}")
        return []
    
    # This is the primary public method for this module
    async def get_full_keyword_runes(self, interest: str, country_code: Optional[str] = None) -> Dict:
        """Orchestrates the gathering of all high-quality keyword runes from the most reliable oracles."""
        logger.info(f"Gathering all potent keyword runes for '{interest}' in '{country_code or 'Global'}'...")
        
        tasks = {
            "google_trends": self.divine_from_google_trends(interest, country_code),
            "keywordtool_io": self.decipher_from_keywordtool_io(interest, country_code),
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        final_data = {}
        for task_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Rune-gathering task '{task_name}' failed for '{interest}': {result}")
                final_data[task_name] = {"error": str(result)}
            else:
                final_data[task_name] = result
        
        return final_data
--- END OF FILE backend/keyword_engine.py ---