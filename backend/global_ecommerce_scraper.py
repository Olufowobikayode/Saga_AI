# --- START OF REFACTORED FILE backend/global_ecommerce_scraper.py ---
import asyncio
import logging
import re
import random
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, quote_plus

from bs4 import BeautifulSoup
import aiohttp
from playwright.async_api import async_playwright, Page, BrowserContext
from fake_useragent import UserAgent

from backend.cache import seer_cache, generate_cache_key

logger = logging.getLogger(__name__)

# Configs remain largely the same, but we can simplify since Playwright handles waits intelligently.
ECOMMERCE_SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "amazon": {
        "status": "enabled",
        "base_url_template": "https://www.amazon.{domain}/s?k={query}",
        "domains": ["com", "co.uk", "de", "fr", "es", "it", "ca", "in", "jp"],
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
        "product_item_selector": 'li.s-item',
        "product_title_selector": '.s-item__title',
        "product_link_attr": 'href',
        "product_price_selector": '.s-item__price',
        "product_sales_history_selector": '.s-item__hotness',
        "seller_name_selector": '.s-item__seller-info-text',
    },
    "aliexpress": {
        "status": "enabled",
        "base_url_template": "https://www.aliexpress.com/wholesale?SearchText={query}",
        "domains": ["com"],
        "product_item_selector": "div[data-pl='product-item']",
        "product_title_selector": "h3",
        "product_link_selector": "a",
        "product_link_attr": 'href',
        "product_price_selector": "div[class*='price-sale']",
        "product_sales_history_selector": "span[class*='trade--trade']",
    }
}

class GlobalMarketplaceOracle:
    """
    Saga's Seer of global commerce, now powered by the swift and stealthy Playwright.
    It divines product information from the great digital marketplaces.
    """
    _playwright_instance = None
    _browser = None

    def __init__(self):
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

    async def _get_browser(self):
        """Initializes and returns a shared, single browser instance."""
        if self._browser and self._browser.is_connected():
            return self._browser
        
        logger.info("Summoning the Playwright browser spirit for the first time...")
        self._playwright_instance = await async_playwright().start()
        # We launch Chromium, as it was installed in the Dockerfile.
        # headless=True is the default but we make it explicit.
        self._browser = await self._playwright_instance.chromium.launch(headless=True)
        return self._browser

    async def _create_stealth_context(self) -> BrowserContext:
        """Creates a new, isolated browser context with stealth properties."""
        browser = await self._get_browser()
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        
        # Playwright's new_context is far more efficient than launching a whole new browser.
        # It's like a fresh, clean incognito session each time.
        context = await browser.new_context(
            user_agent=user_agent,
            java_script_enabled=True,
            # Emulate a common screen size and color scheme
            viewport={'width': 1920, 'height': 1080},
            screen={'width': 1920, 'height': 1080},
            color_scheme='dark',
            locale='en-US'
        )
        # Block common tracking and ad scripts to speed up loading and reduce detection.
        await context.route(re.compile(r"(\.png$)|(\.jpg$)|(google-analytics\.com)|(googletagmanager\.com)"), lambda route: route.abort())
        return context

    async def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetches a page's full HTML content using a stealthy Playwright context."""
        context = await self._create_stealth_context()
        page = None
        try:
            page = await context.new_page()
            logger.info(f"Dispatching stealthy Playwright spirit to read the scroll at {url}...")
            # Use 'networkidle' to wait for most dynamic content to load.
            await page.goto(url, timeout=30000, wait_until='networkidle')
            await page.wait_for_timeout(random.uniform(2000, 4000)) # Human-like pause
            content = await page.content()
            return content
        except Exception as e:
            logger.error(f"The Playwright spirit failed to read the scroll at {url}: {e}")
            return None
        finally:
            if page: await page.close()
            if context: await context.close()

    # The utility functions for parsing data remain the same.
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

    async def run_marketplace_divination(
        self, product_query: str, marketplace_domain: Optional[str] = None,
        max_products: int = 10, target_country_code: Optional[str] = None
    ) -> Dict:
        cache_key = generate_cache_key("run_marketplace_divination", query=product_query, domain=marketplace_domain, country=target_country_code)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None: return cached_results

        target_config = None
        identified_marketplace = "N/A"
        if marketplace_domain:
            for key, config in ECOMMERCE_SITE_CONFIGS.items():
                if key in marketplace_domain:
                    target_config, identified_marketplace = config, key
                    break
        if not target_config: return {"products": [], "identified_marketplace": "Unknown Realm"}

        domain_parts = urlparse(f"http://{marketplace_domain}").hostname.split('.')
        tld = domain_parts[-1]
        domain_to_use = tld if tld in target_config.get("domains", []) else target_config.get("domains", ["com"])[0]
        url = target_config["base_url_template"].format(query=quote_plus(product_query), domain=domain_to_use)
        
        html_content = await self._fetch_with_playwright(url)
        if not html_content:
            return {"products": [], "identified_marketplace": identified_marketplace}

        soup = BeautifulSoup(html_content, 'lxml')
        product_elements = soup.select(target_config["product_item_selector"])[:max_products]
        all_products = []

        for el in product_elements:
            try:
                title = el.select_one(target_config["product_title_selector"]).get_text(strip=True)
                
                link_el = el.select_one(target_config.get("product_link_selector", target_config["product_title_selector"]))
                link = link_el[target_config["product_link_attr"]] if link_el else "#"
                if link and not link.startswith('http'):
                    base_url = urlparse(url)
                    link = f"{base_url.scheme}://{base_url.netloc}{link}"

                price_main_text = el.select_one(target_config["product_price_selector"]).get_text(strip=True) if el.select_one(target_config["product_price_selector"]) else ""
                price_fraction_text_el = el.select_one(target_config.get("product_price_fraction_selector", ""))
                price_fraction_text = price_fraction_text_el.get_text(strip=True) if price_fraction_text_el else ""
                price = self._parse_value(price_main_text, price_fraction_text)

                rating_el = el.select_one(target_config.get("product_rating_selector", ""))
                rating = self._parse_rating(rating_el.get_text(strip=True)) if rating_el else 0.0

                sales_el = el.select_one(target_config.get("product_sales_history_selector", ""))
                sales_history = self._parse_sales_history(sales_el.get_text(strip=True)) if sales_el else 0

                seller_el = el.select_one(target_config.get("seller_name_selector", ""))
                seller_name = seller_el.get_text(strip=True) if seller_el else "An unknown purveyor"
                
                if title and price > 0:
                    all_products.append({
                        "title": title, "price": price, "rating": rating,
                        "sales_history_count": sales_history, "seller_name": seller_name,
                        "link": link, "source_marketplace": identified_marketplace
                    })
            except Exception as item_e:
                logger.debug(f"Failed to divine details for one artifact in {identified_marketplace}: {item_e}")

        final_results = {
            "products": all_products, "identified_marketplace": identified_marketplace,
            "raw_artifacts_found_count": len(all_products)
        }
        seer_cache.set(cache_key, final_results, ttl_seconds=86400)
        return final_results
    
    # This function for reading a user's store can also be simplified.
    async def read_user_store_scroll(self, user_store_url: str) -> Optional[str]:
        cache_key = generate_cache_key("read_user_store_scroll", url=user_store_url)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None: return cached_results
        
        logger.info(f"Attempting to read the user's store scroll from: {user_store_url}")
        
        # We can use Playwright for robust JS-heavy sites or fall back to aiohttp for simple ones.
        html = await self._fetch_with_playwright(user_store_url)
        
        if html:
            soup = BeautifulSoup(html, 'lxml')
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)
            final_text = ' '.join(text.split())[:15000] # Normalize whitespace
            seer_cache.set(cache_key, final_text, ttl_seconds=86400)
            return final_text
        return "Saga's Seer could not read the scroll at the provided URL."