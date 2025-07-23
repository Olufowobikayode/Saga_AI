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

from backend.cache import seer_cache, generate_cache_key

logger = logging.getLogger(__name__)

# ### FINAL UPGRADE: Selectors are now fully robust, with a 'selector_type' to handle CSS or XPath.
ECOMMERCE_SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "amazon": {
        "status": "enabled",
        "selector_type": "css",
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
        "selector_type": "css",
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
        "selector_type": "xpath",
        "base_url_template": "https://www.aliexpress.com/wholesale?SearchText={query}",
        "domains": ["com"],
        "product_wait_selector": "//div[contains(@data-pl, 'product-item')]",
        "product_item_selector": "//div[contains(@data-pl, 'product-item')]",
        "product_title_selector": ".//h3[contains(@class, 'title')]",
        "product_link_selector": ".//a[contains(@href, '/item/')]",
        "product_link_attr": 'href',
        "product_price_selector": ".//div[contains(@class, 'price-sale')]",
        "product_sales_history_selector": ".//span[contains(@class, 'trade--trade')]",
    }
}

# ### ENHANCEMENT: Create a helper function to select elements using either CSS or XPath
def select_one(element, selector: str, selector_type: str):
    if selector_type == 'xpath':
        # lxml's selectolax-like syntax is not standard in bs4, so we use a more compatible approach
        # For simplicity, we'll use a small trick if bs4 is backed by lxml
        # A more robust solution might involve using the lxml library directly
        # But this keeps the code cleaner.
        # Note: BeautifulSoup's .select() is for CSS. For XPath, we need a different approach.
        # Let's use a more direct method with lxml if possible, or adapt.
        # For now, we will assume the element is an lxml element if we need XPath.
        # This part is tricky with just BeautifulSoup. Let's simplify.
        # We will use Selenium's find_element for XPath on sub-elements.
        # This is a clean way to do it without changing the whole parsing logic.
        # This function will now expect a Selenium element.
        try:
            return element.find_element(By.XPATH, selector)
        except:
            return None
    else: # css
        return element.select_one(selector)

class GlobalMarketplaceOracle:
    # ... (init and other methods remain the same)
    def __init__(self):
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

    def _get_driver(self) -> webdriver.Chrome:
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
        stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
        return driver

    async def _fetch_with_selenium(self, url: str, config: Dict) -> Optional[webdriver.Chrome]:
        """Fetches a page with Selenium and returns the driver instance for parsing."""
        driver = None
        try:
            driver = self._get_driver()
            logger.info(f"Dispatching stealthy Chrome spirit to read the scroll at {url}...")
            await asyncio.to_thread(driver.get, url)
            
            by_method = By.XPATH if config['selector_type'] == 'xpath' else By.CSS_SELECTOR
            await asyncio.to_thread(WebDriverWait(driver, 15).until(EC.presence_of_element_located((by_method, config["product_wait_selector"]))))
            
            await asyncio.sleep(random.uniform(2.8, 4.2))
            return driver # Return the live driver
        except Exception as e:
            logger.error(f"The Chrome spirit failed to read the scroll at {url}: {e}")
            if driver:
                await asyncio.to_thread(driver.quit)
            return None

    # ... (aiohttp fetcher and parsers remain the same)
    async def _fetch_html_with_aiohttp(self, url: str) -> Optional[str]:
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        headers = { 'User-Agent': user_agent }
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=15) as response:
                    response.raise_for_status()
                    return await response.text()
        except aiohttp.ClientError as e: return None
        except Exception as e: return None
    def _parse_value(self, price_str: str, fraction_str: Optional[str] = None) -> float:
        if not price_str: return 0.0
        try:
            price_text = re.sub(r'[^\d.]', '', price_str)
            if fraction_str: price_text += '.' + re.sub(r'[^\d]', '', fraction_str)
            return float(price_text) if price_text else 0.0
        except (ValueError, TypeError): return 0.0
    def _parse_rating(self, rating_str: str) -> float:
        if not rating_str: return 0.0
        try:
            match = re.search(r'(\d[\d,.]*)', rating_str.replace(',', '.'))
            return float(match.group(1)) if match else 0.0
        except (ValueError, TypeError): return 0.0
    def _parse_sales_history(self, sales_str: str) -> int:
        if not sales_str: return 0
        try:
            sales_str = sales_str.lower().replace('sold', '').replace('+', '').replace(',', '').strip()
            num_part = re.search(r'(\d[\d,.]*)', sales_str)
            if not num_part: return 0
            num = float(num_part.group(1))
            if 'k' in sales_str: num *= 1000
            elif 'm' in sales_str: num *= 1_000_000
            return int(num)
        except (ValueError, TypeError): return 0

    async def run_marketplace_divination(self,
                                         product_query: str,
                                         marketplace_domain: Optional[str] = None,
                                         max_products: int = 10,
                                         target_country_code: Optional[str] = None) -> Dict:
        cache_key = generate_cache_key("run_marketplace_divination", query=product_query, domain=marketplace_domain, country=target_country_code)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None: return cached_results

        target_config = None
        identified_marketplace = "N/A"
        if marketplace_domain:
            for key, config in ECOMMERCE_SITE_CONFIGS.items():
                if key in marketplace_domain:
                    target_config = config
                    identified_marketplace = key
                    break
        if not target_config: return {"products": [], "identified_marketplace": "Unknown Realm"}

        domain_parts = urlparse(f"http://{marketplace_domain}").hostname.split('.')
        tld = domain_parts[-1]
        domain_to_use = tld if tld in target_config.get("domains", []) else target_config.get("domains", ["com"])[0]
        url = target_config["base_url_template"].format(query=quote_plus(product_query), domain=domain_to_use)
        
        all_products = []
        driver = None
        
        # ### REFACTOR: We will now use Selenium for all parsing to handle XPath correctly.
        # This is a more robust approach than trying to mix BeautifulSoup and Selenium parsing.
        driver = await self._fetch_with_selenium(url, target_config)
        
        if not driver:
            logger.error(f"The Selenium spirit failed to retrieve the scroll from {url}.")
            return {"products": [], "identified_marketplace": identified_marketplace}

        try:
            selector_type = target_config["selector_type"]
            by_method = By.XPATH if selector_type == 'xpath' else By.CSS_SELECTOR
            
            product_elements = await asyncio.to_thread(driver.find_elements, by_method, target_config["product_item_selector"])

            for el in product_elements[:max_products]:
                try:
                    # Use a helper to find sub-elements, abstracting away CSS vs XPath
                    def find_sub_element_text(selector_key):
                        sub_el = select_one(el, target_config[selector_key], selector_type)
                        return sub_el.text.strip() if sub_el else ""

                    def find_sub_element_attr(selector_key, attr):
                        sub_el = select_one(el, target_config[selector_key], selector_type)
                        return sub_el.get_attribute(attr) if sub_el else ""

                    title = find_sub_element_text("product_title_selector")
                    link = find_sub_element_attr("product_link_selector", target_config["product_link_attr"])
                    
                    if link and not link.startswith('http'):
                        base_url = f"https://www.{identified_marketplace}.{domain_to_use}"
                        link = f"{base_url}{link}"

                    price_main_text = find_sub_element_text("product_price_selector")
                    price_fraction_text = find_sub_element_text("product_price_fraction_selector") if "product_price_fraction_selector" in target_config else ""
                    price = self._parse_value(price_main_text, price_fraction_text)

                    rating = self._parse_rating(find_sub_element_text("product_rating_selector") if "product_rating_selector" in target_config else "")
                    sales_history = self._parse_sales_history(find_sub_element_text("product_sales_history_selector") if "product_sales_history_selector" in target_config else "")
                    seller_name = find_sub_element_text("seller_name_selector") if "seller_name_selector" in target_config else "An unknown purveyor"

                    if price > 0:
                        all_products.append({
                            "title": title, "price": price, "rating": rating,
                            "sales_history_count": sales_history, "seller_name": seller_name,
                            "link": link, "source_marketplace": identified_marketplace
                        })
                except Exception as item_e:
                    logger.debug(f"Failed to divine all details for one artifact in {identified_marketplace}: {item_e}")
                    continue
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)

        worthy_artifacts = [p for p in all_products if p.get('rating', 0.0) >= 4.0]
        sorted_artifacts = sorted(worthy_artifacts, key=lambda x: (-x.get('rating', 0.0), -x.get('sales_history_count', 0), x.get('price', float('inf'))))
        
        final_results = {
            "products": sorted_artifacts,
            "identified_marketplace": identified_marketplace,
            "raw_artifacts_found_count": len(all_products)
        }
        seer_cache.set(cache_key, final_results, ttl_seconds=86400)
        return final_results

    async def read_user_store_scroll(self, user_store_url: str) -> Optional[str]:
        cache_key = generate_cache_key("read_user_store_scroll", url=user_store_url)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None: return cached_results
        
        logger.info(f"Attempting to read the user's store scroll from: {user_store_url}")
        
        # For this generic function, we will use BeautifulSoup with lxml as it's faster and sufficient.
        html = await self._fetch_html_with_aiohttp(user_store_url)
        if not html:
            driver = await self._fetch_with_selenium(user_store_url, {"selector_type": "css", "product_wait_selector": "body"})
            if driver:
                html = driver.page_source
                await asyncio.to_thread(driver.quit)

        if html:
            soup = BeautifulSoup(html, 'lxml') # Use the fast lxml parser
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)
            final_text = text[:15000]
            seer_cache.set(cache_key, final_text, ttl_seconds=86400)
            return final_text
        return None