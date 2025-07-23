import asyncio
import logging
import re
import random
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

from selenium_stealth import stealth
from fake_useragent import UserAgent

# ### FIX: Import the caching utilities
from backend.cache import seer_cache, generate_cache_key

logger = logging.getLogger(__name__)

ECOMMERCE_SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "amazon": {
        "status": "enabled",
        "base_url_template": "https://www.amazon.{domain}/s?k={query}",
        "domains": ["com", "co.uk", "de", "fr", "es", "it", "ca", "in", "jp"],
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
        "product_wait_selector": 'div[data-role="product-item"]',
        "product_item_selector": 'div[data-role="product-item"]',
        "product_title_selector": 'h3.manhattan--titleText--2S8kGjB',
        "product_link_selector": 'a.manhattan--container--1lP57Ag',
        "product_link_attr": 'href',
        "product_price_selector": '.manhattan--price-sale--1CCSZfK',
        "product_sales_history_selector": '.manhattan--trade--2cIXdEw',
    }
}


class GlobalMarketplaceOracle:
    """
    Saga's primary Seer for the realms of commerce.
    This oracle is responsible for scraping product information from global e-commerce platforms.
    It now includes stealth evasion techniques and a long-lived cache to ensure reliability and performance.
    """

    def __init__(self):
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

    def _get_driver(self) -> webdriver.Chrome:
        """Summons an enhanced, stealthy Chrome spirit for its journey."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")
        
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        
        return driver

    async def _fetch_html_with_selenium(self, url: str) -> Optional[str]:
        """Fetches the fully rendered scroll of a URL using an enhanced Chrome spirit."""
        driver = None
        try:
            driver = self._get_driver()
            logger.info(f"Dispatching stealthy Chrome spirit to read the scroll at {url}...")
            await asyncio.to_thread(driver.get, url)
            await asyncio.to_thread(WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))))
            await asyncio.sleep(random.uniform(2.8, 4.2))
            return await asyncio.to_thread(lambda: driver.page_source)
        except Exception as e:
            logger.error(f"The Chrome spirit failed to read the scroll at {url}: {e}")
            return None
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)

    async def _fetch_html_with_aiohttp(self, url: str) -> Optional[str]:
        """Fetches the raw HTML of a scroll using a swift raven (aiohttp)."""
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        headers = { 'User-Agent': user_agent }
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
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
        if not price_str: return 0.0
        try:
            price_text = re.sub(r'[^\d.]', '', price_str)
            if fraction_str:
                price_text += '.' + re.sub(r'[^\d]', '', fraction_str)
            return float(price_text) if price_text else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _parse_rating(self, rating_str: str) -> float:
        if not rating_str: return 0.0
        try:
            match = re.search(r'(\d[\d,.]*)', rating_str.replace(',', '.'))
            return float(match.group(1)) if match else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _parse_sales_history(self, sales_str: str) -> int:
        if not sales_str: return 0
        try:
            sales_str = sales_str.lower().replace('sold', '').replace('+', '').replace(',', '').strip()
            num_part = re.search(r'(\d[\d,.]*)', sales_str)
            if not num_part: return 0
            
            num = float(num_part.group(1))
            if 'k' in sales_str:
                num *= 1000
            elif 'm' in sales_str:
                num *= 1_000_000
            return int(num)
        except (ValueError, TypeError):
            return 0

    async def run_marketplace_divination(self,
                                         product_query: str,
                                         marketplace_domain: Optional[str] = None,
                                         max_products: int = 10,
                                         target_country_code: Optional[str] = None) -> Dict:
        """
        Casts its sight upon a configured marketplace to read the sagas of its artifacts.
        This operation is cached for 24 hours to protect against IP blocks.
        """
        # ### ENHANCEMENT: Implement caching for this expensive operation.
        cache_key = generate_cache_key("run_marketplace_divination", query=product_query, domain=marketplace_domain, country=target_country_code)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        all_products = []
        identified_marketplace = "N/A"

        target_config = None
        if marketplace_domain:
            for key, config in ECOMMERCE_SITE_CONFIGS.items():
                if key in marketplace_domain:
                    target_config = config
                    identified_marketplace = key
                    break
        
        if not target_config or target_config['status'] != 'enabled':
             logger.warning(f"No enabled realm of commerce found for domain: {marketplace_domain}")
             return {"products": [], "identified_marketplace": "Unknown Realm"}

        domain_parts = urlparse(f"http://{marketplace_domain}").hostname.split('.')
        tld = domain_parts[-1]
        domain_to_use = tld if tld in target_config.get("domains", []) else target_config.get("domains", ["com"])[0]

        url = target_config["base_url_template"].format(query=quote_plus(product_query), domain=domain_to_use)
        logger.info(f"Casting gaze upon the realm of {identified_marketplace} for artifacts matching '{product_query}'...")
        
        html = await self._fetch_html_with_aiohttp(url)
        if not html:
            html = await self._fetch_html_with_selenium(url)
        
        if not html:
            logger.error(f"Both raven and spirit failed to read the scroll from {url}.")
            return {"products": [], "identified_marketplace": identified_marketplace}

        soup = BeautifulSoup(html, 'html.parser')
        product_elements = soup.select(target_config["product_item_selector"])

        for el in product_elements[:max_products]:
            try:
                title_el = el.select_one(target_config["product_title_selector"])
                title = title_el.text.strip() if title_el else "An artifact with no name"

                link_el = el.select_one(target_config.get("product_link_selector", target_config["product_title_selector"]))
                link = ""
                if link_el and link_el.has_attr(target_config["product_link_attr"]):
                    link = link_el[target_config["product_link_attr"]]
                
                if link and not link.startswith('http'):
                    base_url = f"https://www.{identified_marketplace}.{domain_to_use}"
                    link = f"{base_url}{link}"

                price_main_el = el.select_one(target_config["product_price_selector"])
                price_fraction_el = el.select_one(target_config.get("product_price_fraction_selector", ""))
                price_main_text = price_main_el.text if price_main_el else ""
                price_fraction_text = price_fraction_el.text if price_fraction_el else ""
                price = self._parse_value(price_main_text, price_fraction_text)

                rating_el = el.select_one(target_config.get("product_rating_selector", ""))
                rating = self._parse_rating(rating_el.text) if rating_el else 0.0

                sales_el = el.select_one(target_config.get("product_sales_history_selector", ""))
                sales_history = self._parse_sales_history(sales_el.text) if sales_el else 0

                seller_el = el.select_one(target_config.get("seller_name_selector", ""))
                seller_name = seller_el.text.strip() if seller_el else "An unknown purveyor"

                if price > 0:
                    all_products.append({
                        "title": title, "price": price, "rating": rating,
                        "sales_history_count": sales_history, "seller_name": seller_name,
                        "link": link, "source_marketplace": identified_marketplace
                    })
            except Exception as item_e:
                logger.debug(f"Failed to divine all details for one artifact in {identified_marketplace}: {item_e}")
                continue

        worthy_artifacts = [p for p in all_products if p.get('rating', 0.0) >= 4.0]
        sorted_artifacts = sorted(worthy_artifacts, key=lambda x: (-x.get('rating', 0.0), -x.get('sales_history_count', 0), x.get('price', float('inf'))))
        
        final_results = {
            "products": sorted_artifacts,
            "identified_marketplace": identified_marketplace,
            "raw_artifacts_found_count": len(all_products)
        }

        # ### ENHANCEMENT: Set the result in the cache with a long TTL (24 hours = 86400 seconds).
        seer_cache.set(cache_key, final_results, ttl_seconds=86400)

        return final_results

    async def read_user_store_scroll(self, user_store_url: str) -> Optional[str]:
        """
        Reads the general text from a user's store scroll for the AI to analyze its tone and style.
        This operation is also cached.
        """
        # ### ENHANCEMENT: Implement caching for this expensive operation.
        cache_key = generate_cache_key("read_user_store_scroll", url=user_store_url)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        logger.info(f"Attempting to read the user's store scroll from: {user_store_url}")
        
        content = await self._fetch_html_with_aiohttp(user_store_url)
        if not content:
            logger.warning(f"The raven could not read the scroll, dispatching a more powerful Chrome spirit to {user_store_url}")
            content = await self._fetch_html_with_selenium(user_store_url)

        if content:
            soup = BeautifulSoup(content, 'html.parser')
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)
            final_text = text[:15000]
            
            # ### ENHANCEMENT: Set the result in the cache with a long TTL (24 hours = 86400 seconds).
            seer_cache.set(cache_key, final_text, ttl_seconds=86400)
            
            return final_text
        
        return None