--- START OF FILE backend/global_ecommerce_scraper.py ---
import asyncio
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import aiohttp

logger = logging.getLogger(__name__)

# --- SAGA'S ATLAS OF COMMERCE REALMS ---
# This sacred scroll maps the pathways and runes needed to divine wisdom from global marketplaces.
# Saga's Insight: The stability of these runes varies. Those bound to data attributes are strong,
# while those tied to fleeting styles are as fickle as the winds. They must be checked often.
ECOMMERCE_SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "amazon": { # A general key for all Amazonian realms
        "status": "enabled",
        "base_url_template": "https://www.amazon.{domain}/s?k={query}",
        "domains": ["com", "co.uk", "de", "fr", "es", "it", "ca", "in", "jp"],
        # ROBUST SELECTORS: Based on data attributes, less likely to change.
        "product_wait_selector": '[data-cel-widget="search_result_s-result-list"]',
        "product_item_selector": 'div.s-result-item[data-asin]',
        "product_title_selector": 'h2 a.a-link-normal',
        "product_link_attr": 'href',
        "product_price_selector": 'span.a-price-whole',
        "product_price_fraction_selector": 'span.a-price-fraction',
        "product_rating_selector": 'i.a-icon-star-small span.a-icon-alt',
        "seller_name_selector": '.a-row.a-size-small.a-color-secondary',
    },
    "ebay": {
        "status": "enabled",
        "base_url_template": "https://www.ebay.com/sch/i.html?_nkw={query}",
        "domains": ["com"],
        # STABLE SELECTORS: Based on core item wrappers and info sections.
        "product_wait_selector": '.s-item__info',
        "product_item_selector": '.s-item__wrapper',
        "product_title_selector": '.s-item__title',
        "product_link_attr": 'href',
        "product_price_selector": '.s-item__price',
        "product_sales_history_selector": '.s-item__hotness .s-item__bid .s-item__bids.s-item__bidCount',
        "seller_name_selector": '.s-item__seller-info .s-item__seller-info-text',
    },
    "aliexpress": {
        "status": "enabled",
        "base_url_template": "https://www.aliexpress.com/wholesale?SearchText={query}",
        "domains": ["com"],
        # FRAGILE SELECTORS: These are auto-generated and will likely break often. High maintenance required.
        "product_wait_selector": 'div[data-role="product-item"]',
        "product_item_selector": 'div[data-role="product-item"]',
        "product_title_selector": '.manhattan--titleText--2S8kGjB', # Example of fragile, auto-gen class
        "product_link_attr": 'href',
        "product_price_selector": '.manhattan--price-sale--1CCSZfK', # Example of fragile, auto-gen class
        "product_sales_history_selector": '.manhattan--trade--2cIXdEw', # Example of fragile, auto-gen class
    }
}


class GlobalMarketplaceOracle:
    """
    A specialized oracle within the SagaEngine, whose sight pierces the veils
    of global marketplaces. It divines the value, history, and standing of
    commercial artifacts (products) and their purveyors.
    """

    def _get_driver(self) -> webdriver.Chrome:
        """Summons a Chrome spirit for its journey into the realms of commerce."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    async def _fetch_html_with_selenium(self, url: str) -> Optional[str]:
        """Fetches the fully rendered scroll of a URL using a Chrome spirit."""
        driver = None
        try:
            driver = self._get_driver()
            logger.info(f"Dispatching Chrome spirit to read the scroll at {url}...")
            await asyncio.to_thread(driver.get, url)
            await asyncio.to_thread(WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))))
            await asyncio.sleep(3) # Allow time for the final verses of the scroll to be written (JS rendering).
            return await asyncio.to_thread(lambda: driver.page_source)
        except Exception as e:
            logger.error(f"The Chrome spirit failed to read the scroll at {url}: {e}")
            return None
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)

    async def _fetch_text_with_aiohttp(self, url: str) -> Optional[str]:
        """Fetches the raw text of a scroll using a swift raven (aiohttp)."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    response.raise_for_status()
                    return await response.text()
        except aiohttp.ClientError as e:
            logger.warning(f"A raven failed to retrieve the scroll from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected disturbance occurred while sending a raven to {url}: {e}")
            return None

    def _parse_value(self, price_str: str, fraction_str: Optional[str] = None) -> float:
        """A rune to decipher the value from strings of text."""
        try:
            full_price_str = price_str.replace(',', '').replace('$', '').strip()
            if fraction_str:
                full_price_str += '.' + fraction_str.strip()
            return float(full_price_str)
        except (ValueError, TypeError):
            logger.debug(f"The value of an artifact was shrouded in mystery: '{price_str}'")
            return 0.0

    def _parse_rating(self, rating_str: str) -> float:
        """A rune to decipher the greatness of an artifact from text."""
        try:
            # Handles "4.5 out of 5 stars" format
            if "out of 5" in rating_str:
                return float(rating_str.split(' ')[0])
            return float(rating_str)
        except (ValueError, TypeError):
            logger.debug(f"The greatness of an artifact was indecipherable: '{rating_str}'")
            return 0.0

    def _parse_sales_history(self, sales_str: str) -> int:
        """A rune to decipher the sales saga of an artifact."""
        try:
            sales_str = sales_str.lower().replace('sold', '').replace('+', '').replace(',', '').strip()
            return int(sales_str.split(' ')[0]) # Handle cases like "5k sold"
        except (ValueError, TypeError):
            logger.debug(f"The sales saga of an artifact was unclear: '{sales_str}'")
            return 0

    async def divine_from_marketplaces(self,
                                       product_query: str,
                                       marketplace_domain: Optional[str] = None,
                                       max_products: int = 20,
                                       target_country_code: Optional[str] = None) -> Dict:
        """
        Casts its sight upon one or more configured marketplaces to read the sagas of their artifacts.
        """
        driver = None
        all_products = []
        identified_marketplace = "N/A"

        try:
            driver = self._get_driver()
            target_configs = {}
            domain_key = marketplace_domain.split('.')[-1] if marketplace_domain and '.' in marketplace_domain else marketplace_domain
            
            # Find the matching config for the provided domain
            for site_key, config in ECOMMERCE_SITE_CONFIGS.items():
                if marketplace_domain and site_key in marketplace_domain:
                    target_configs[site_key] = config
                    identified_marketplace = site_key
                    break
            
            if not target_configs:
                 logger.warning(f"No configured realm of commerce found for domain: {marketplace_domain}")
                 return {"products": [], "identified_marketplace": "Unknown Realm"}

            for site_key, config in target_configs.items():
                domain_to_use = domain_key if domain_key in config["domains"] else config["domains"][0]
                url = config["base_url_template"].format(query=quote_plus(product_query), domain=domain_to_use)
                logger.info(f"Casting gaze upon the realm of {site_key} for artifacts matching '{product_query}'...")
                
                await asyncio.to_thread(driver.get, url)
                await asyncio.to_thread(WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["product_wait_selector"]))))
                await asyncio.sleep(3)

                product_elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["product_item_selector"])

                for el in product_elements[:max_products]:
                    try:
                        title_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["product_title_selector"])
                        title = await asyncio.to_thread(lambda: title_els[0].text.strip()) if title_els else "An artifact with no name"
                        link = await asyncio.to_thread(lambda: title_els[0].get_attribute(config["product_link_attr"])) if title_els else "A path unknown"

                        # Value (Price) Divination
                        price_main_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["product_price_selector"])
                        price_fraction_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config.get("product_price_fraction_selector", " ")))
                        price_fraction = await asyncio.to_thread(lambda: price_fraction_els[0].text) if price_fraction_els else None
                        price = self._parse_value(await asyncio.to_thread(lambda: price_main_els[0].text), price_fraction) if price_main_els else 0.0

                        # Greatness (Rating) Divination
                        rating_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config.get("product_rating_selector", " ")))
                        rating_text = await asyncio.to_thread(lambda: rating_els[0].text) if rating_els else ""
                        rating = self._parse_rating(rating_text)

                        # Sales Saga Divination
                        sales_history = 0
                        if config.get("product_sales_history_selector"):
                            sales_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["product_sales_history_selector"]))
                            sales_text = await asyncio.to_thread(lambda: sales_els[0].text) if sales_els else ""
                            sales_history = self._parse_sales_history(sales_text)
                        
                        seller_name = "An unknown purveyor"
                        if config.get("seller_name_selector"):
                            seller_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["seller_name_selector"]))
                            seller_name = await asyncio.to_thread(lambda: seller_els[0].text.strip()) if seller_els else seller_name

                        all_products.append({
                            "title": title, "price": price, "rating": rating,
                            "sales_history_count": sales_history, "seller_name": seller_name,
                            "link": link, "source_marketplace": site_key
                        })
                    except Exception as item_e:
                        logger.debug(f"Failed to divine all details for one artifact in {site_key}: {item_e}")
                        continue
        except Exception as e:
            logger.error(f"A great disturbance clouded the vision of the marketplaces for '{product_query}': {e}")
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)

        # Saga's Judgment: Filter for worthy artifacts and sort them by greatness, then sales, then value.
        worthy_artifacts = [p for p in all_products if p['rating'] >= 4.0 and p['price'] > 0]
        sorted_artifacts = sorted(worthy_artifacts, key=lambda x: (-x['rating'], -x['sales_history_count'], x['price']))
        
        return {
            "products": sorted_artifacts[:max_products],
            "identified_marketplace": identified_marketplace,
            "raw_artifacts_found_count": len(all_products)
        }

    async def read_user_store_scroll(self, user_store_url: str) -> Optional[str]:
        """
        Reads the general text from a user's store scroll for the AI to analyze its tone and style.
        Uses a swift raven (aiohttp) first, falling back to a Chrome spirit for complex scrolls.
        """
        logger.info(f"Attempting to read the user's store scroll from: {user_store_url}")
        
        content = await self._fetch_text_with_aiohttp(user_store_url)
        if not content:
            logger.warning(f"The raven could not read the scroll, dispatching a more powerful Chrome spirit to {user_store_url}")
            content = await self._fetch_html_with_selenium(user_store_url)

        if content:
            soup = BeautifulSoup(content, 'html.parser')
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            return clean_text[:15000] # Return the first 15,000 characters of the scroll.
        
        return None
--- END OF FILE backend/global_ecommerce_scraper.py ---