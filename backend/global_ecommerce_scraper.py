--- START OF FILE backend/global_ecommerce_scraper.py ---
import asyncio
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup # Added for better HTML parsing

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import aiohttp # For fetching user store content without full browser

logger = logging.getLogger(__name__)

# --- GLOBAL E-COMMERCE SITE CONFIGURATION ---
# This dictionary defines how to scrape different global e-commerce platforms.
# Extending this for many more platforms is a significant ongoing development task.
# Each entry needs specific CSS selectors for products, sellers, prices, ratings, etc.
# Note: These selectors are examples and might break if the websites change.
# You MUST test these selectors regularly.
ECOMMERCE_SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "amazon": { # General key for all Amazon domains
        "status": "enabled",
        "base_url_template": "https://www.amazon.{domain}/s?k={query}",
        "domains": ["com", "co.uk", "de", "fr", "es", "it", "ca", "in", "jp"], # Supported Amazon domains
        "product_wait_selector": '[data-cel-widget="search_result_s-result-list"]',
        "product_item_selector": 'div.s-result-item[data-asin]', # Main product container
        "product_title_selector": 'h2 a.a-link-normal',
        "product_link_attr": 'href',
        "product_price_selector": 'span.a-price-whole', # Price before decimal
        "product_price_fraction_selector": 'span.a-price-fraction', # Price after decimal
        "product_rating_selector": 'i.a-icon-star-small span.a-icon-alt', # e.g., "4.5 out of 5 stars"
        "product_sales_history_selector": None, # Amazon doesn't expose exact sales history easily on search results
        "seller_name_selector": '.a-row.a-size-small.a-color-secondary', # Often refers to brand/seller text
        "seller_years_on_platform_selector": None, # Rarely exposed on product listings
        "next_page_selector": 'a.s-pagination-next',
    },
    "ebay": {
        "status": "enabled",
        "base_url_template": "https://www.ebay.com/sch/i.html?_nkw={query}", # eBay.com covers many global listings
        "domains": ["com"], # Can add others like co.uk, de etc. if structure differs significantly
        "product_wait_selector": '.s-item__info',
        "product_item_selector": '.s-item__wrapper',
        "product_title_selector": '.s-item__title',
        "product_link_attr": 'href',
        "product_price_selector": '.s-item__price',
        "product_rating_selector": '.star-rating-count span', # e.g., "(123)" - need to parse count
        "product_sales_history_selector": '.s-item__hotness .s-item__bid .s-item__bids.s-item__bidCount', # e.g., "5 sold"
        "seller_name_selector": '.s-item__seller-info .s-item__seller-info-text',
        "seller_years_on_platform_selector": None,
        "next_page_selector": '.pagination__next',
    },
    "aliexpress": {
        "status": "enabled",
        "base_url_template": "https://www.aliexpress.com/wholesale?SearchText={query}",
        "domains": ["com"],
        "product_wait_selector": 'div[data-role="product-item"]',
        "product_item_selector": 'div[data-role="product-item"]',
        "product_title_selector": '.manhattan--text--3Ua5JpW',
        "product_link_attr": 'href',
        "product_price_selector": '.manhattan--price-dot--cXxJmIT span[data-mark="p_price"]', # Main price
        "product_price_range_selector": '.manhattan--price-dot--cXxJmIT', # Might be a price range
        "product_rating_selector": '.manhattan--rating-panel--10gsO_Q .comet-icon-star-on', # Star icons for visual count
        "product_sales_history_selector": '.manhattan--trade--2pgZ6ht', # e.g., "Sold 100+"
        "seller_name_selector": None, # Often not easily available from search results for individual sellers
        "seller_years_on_platform_selector": None,
        "next_page_selector": 'button.next-btn.next-next', # Aliexpress pagination is complex, this is basic
    }
}


class GlobalEcommerceScraper:
    """
    A specialized scraper for global e-commerce marketplaces.
    Focuses on product sourcing and seller analysis.
    """

    def _get_driver(self) -> webdriver.Chrome:
        """Initializes a headless Chrome browser instance for scraping."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    async def _fetch_html_content_selenium(self, url: str) -> Optional[str]:
        """Fetches the full rendered HTML content of a URL using Selenium."""
        driver = None
        try:
            driver = self._get_driver()
            logger.info(f"Fetching HTML content for {url} via Selenium...")
            await asyncio.to_thread(driver.get, url)
            # Wait for some common body element to ensure page is loaded
            await asyncio.to_thread(WebDriverWait(driver, 15).until,
                                   EC.presence_of_element_located((By.TAG_NAME, 'body')))
            await asyncio.sleep(3) # Give extra time for dynamic content
            return await asyncio.to_thread(lambda: driver.page_source)
        except Exception as e:
            logger.error(f"Failed to fetch HTML content for {url} with Selenium: {e}")
            return None
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)

    async def _fetch_text_content_aiohttp(self, url: str) -> Optional[str]:
        """Fetches plain text content from a URL using aiohttp."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    response.raise_for_status()
                    return await response.text()
        except aiohttp.ClientError as e:
            logger.warning(f"Failed to fetch text content from {url} with aiohttp: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching {url} with aiohttp: {e}")
            return None

    def _parse_price(self, price_str: str, fraction_str: Optional[str] = None) -> float:
        """Helper to parse price strings into floats."""
        try:
            full_price_str = price_str.replace(',', '').replace('$', '').strip()
            if fraction_str:
                full_price_str += '.' + fraction_str.strip()
            return float(full_price_str)
        except (ValueError, TypeError):
            logger.debug(f"Could not parse price from '{price_str}' (fraction: '{fraction_str}')")
            return 0.0 # Return 0.0 or a sentinel for unparseable prices

    def _parse_rating(self, rating_str: str) -> float:
        """Helper to parse rating strings (e.g., "4.5 out of 5 stars", "(123)")"""
        try:
            if "out of 5 stars" in rating_str:
                return float(rating_str.split(' ')[0])
            elif rating_str.startswith('(') and rating_str.endswith(')'):
                # For eBay, where rating might be a count, interpret as high rating if count is good
                # This is a heuristic, adjust as needed.
                count = int(rating_str.strip('()'))
                return 4.0 if count > 50 else (3.0 if count > 10 else 0.0) # Heuristic
            return float(rating_str)
        except (ValueError, TypeError):
            logger.debug(f"Could not parse rating from '{rating_str}'")
            return 0.0

    def _parse_sales_history(self, sales_str: str) -> int:
        """Helper to parse sales history strings (e.g., "100+ sold", "5 sold")"""
        try:
            sales_str = sales_str.lower().replace('sold', '').replace('+', '').strip()
            return int(sales_str)
        except (ValueError, TypeError):
            logger.debug(f"Could not parse sales history from '{sales_str}'")
            return 0


    async def scrape_marketplace_listings(self, 
                                          product_query: str, 
                                          marketplace_domain: Optional[str] = None, 
                                          max_products: int = 20) -> Dict:
        """
        Scrapes product listings from one or more configured marketplaces.
        If marketplace_domain is provided, it tries to scrape from that specific one.
        Otherwise, it tries a few enabled global ones.
        """
        driver = None
        all_products = []
        identified_marketplace = "N/A"

        try:
            driver = self._get_driver()
            target_configs = {}

            if marketplace_domain:
                # Find the matching config for the provided domain
                for site_key, config in ECOMMERCE_SITE_CONFIGS.items():
                    # Check if any part of the domain in config matches the provided domain
                    if config["status"] == "enabled" and any(d in marketplace_domain for d in config["domains"]):
                        target_configs[site_key] = config
                        identified_marketplace = site_key # Track which marketplace was targeted
                        break # Only target one specific marketplace if provided
                if not target_configs:
                    logger.warning(f"No enabled configuration found for provided marketplace domain: {marketplace_domain}")
                    return {"products": [], "identified_marketplace": "No match"}
            else:
                # If no specific marketplace, try all enabled ones (or a curated list)
                target_configs = {k: v for k, v in ECOMMERCE_SITE_CONFIGS.items() if v["status"] == "enabled"}
                if not target_configs:
                    logger.warning("No enabled marketplace configurations found.")
                    return {"products": [], "identified_marketplace": "None configured"}
                identified_marketplace = "Multiple (Scraped top results)" # Indicate general search

            for site_key, config in target_configs.items():
                if not config.get("base_url_template") or not config.get("product_item_selector"):
                    logger.warning(f"Skipping {site_key}: Incomplete configuration.")
                    continue

                domain_to_use = marketplace_domain if marketplace_domain and site_key == identified_marketplace else config["domains"][0] # Use specific domain or default
                current_url = config["base_url_template"].format(query=quote_plus(product_query), domain=domain_to_use)
                logger.info(f"Navigating to {site_key} for '{product_query}' at {current_url}...")
                
                products_from_site = []
                pages_scraped = 0
                max_pages_per_site = 2 # Limit pages to scrape per site to manage load

                while len(products_from_site) < max_products and pages_scraped < max_pages_per_site:
                    try:
                        await asyncio.to_thread(driver.get, current_url)
                        await asyncio.to_thread(WebDriverWait(driver, 20).until,
                                               EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["product_wait_selector"])))
                        await asyncio.sleep(3) # Allow JS to render fully

                        product_elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["product_item_selector"])

                        for el in product_elements:
                            if len(products_from_site) >= max_products:
                                break
                            
                            try:
                                title_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["product_title_selector"])
                                title = await asyncio.to_thread(lambda: title_els[0].text.strip()) if title_els else "N/A"
                                link = await asyncio.to_thread(title_els[0].get_attribute, config["product_link_attr"]) if title_els else "N/A"

                                price = 0.0
                                # Price parsing logic
                                price_main_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["product_price_selector"])
                                if price_main_els:
                                    price_fraction_els = []
                                    if config.get("product_price_fraction_selector"):
                                        price_fraction_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["product_price_fraction_selector"])
                                    price_fraction = await asyncio.to_thread(lambda: price_fraction_els[0].text) if price_fraction_els else None
                                    price = self._parse_price(await asyncio.to_thread(lambda: price_main_els[0].text), price_fraction)
                                elif config.get("product_price_range_selector"):
                                     price_range_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["product_price_range_selector"])
                                     if price_range_els:
                                         price_text = await asyncio.to_thread(lambda: price_range_els[0].text.strip())
                                         if '-' in price_text:
                                             price = self._parse_price(price_text.split('-')[0])
                                         else:
                                             price = self._parse_price(price_text)

                                rating_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["product_rating_selector"])
                                rating = 0.0
                                if rating_els:
                                    # Attempt to get aria-label first, then text
                                    aria_label = await asyncio.to_thread(rating_els[0].get_attribute, 'aria-label')
                                    if aria_label:
                                        rating = self._parse_rating(aria_label)
                                    else:
                                        rating = self._parse_rating(await asyncio.to_thread(lambda: rating_els[0].text))
                                
                                sales_history = 0
                                if config["product_sales_history_selector"]:
                                    sales_history_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["product_sales_history_selector"])
                                    if sales_history_els:
                                        sales_history = self._parse_sales_history(await asyncio.to_thread(lambda: sales_history_els[0].text))

                                seller_name = "N/A"
                                if config["seller_name_selector"]:
                                    seller_name_els = await asyncio.to_thread(el.find_elements, By.CSS_SELECTOR, config["seller_name_selector"])
                                    if seller_name_els:
                                        seller_name = await asyncio.to_thread(lambda: seller_name_els[0].text.strip())

                                products_from_site.append({
                                    "title": title,
                                    "price": price,
                                    "rating": rating,
                                    "sales_history_count": sales_history, # Store as int for sorting
                                    "seller_name": seller_name,
                                    "link": link,
                                    "source_marketplace": site_key
                                })
                            except Exception as item_e:
                                logger.debug(f"Could not parse all details for a product item on {site_key}: {item_e}")
                                continue # Skip malformed product entries
                        
                        pages_scraped += 1
                        # Check for next page
                        next_page_elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, config["next_page_selector"])
                        if next_page_elements and await asyncio.to_thread(next_page_elements[0].is_displayed) and await asyncio.to_thread(next_page_elements[0].get_attribute, 'href'):
                            current_url = await asyncio.to_thread(next_page_elements[0].get_attribute, 'href')
                            logger.info(f"Navigating to next page on {site_key}: {current_url}")
                        else:
                            logger.info(f"No more pages found or last page reached on {site_key}.")
                            break # No next page
                        
                    except Exception as e_page:
                        logger.error(f"Error scraping page {pages_scraped+1} on {site_key} for query '{product_query}'. Error: {e_page}")
                        break # Stop if page scraping fails

                all_products.extend(products_from_site)

        except Exception as e:
            logger.error(f"Overall error during marketplace scraping for '{product_query}': {e}")
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)
        
        # Filter for at least 4-star rating and sort:
        # Sort by rating (desc), then sales history (desc), then price (asc)
        filtered_products = [p for p in all_products if p['rating'] >= 4.0 and p['price'] > 0] # Ensure price is valid
        sorted_products = sorted(filtered_products, 
                                 key=lambda x: (x['rating'], x['sales_history_count'], x['price']), 
                                 reverse=True) # Reverse rating and sales history, price asc (implicitly because it's last in tuple and reverse=True only applies to entire tuple)
        
        # Correct sorting for price (ascending) while others are descending
        # We need a custom sort key or sort in multiple passes
        sorted_products = sorted(filtered_products, 
                                 key=lambda x: (-x['rating'], -x['sales_history_count'], x['price']))
        
        return {
            "products": sorted_products[:max_products], # Return up to max_products
            "identified_marketplace": identified_marketplace,
            "raw_products_found_count": len(all_products)
        }

    async def get_user_store_content(self, user_store_url: str) -> Optional[str]:
        """
        Fetches general text content from a user's store URL for AI analysis.
        Uses aiohttp for lighter fetching, but falls back to Selenium if needed.
        """
        logger.info(f"Attempting to fetch user store content from: {user_store_url}")
        
        # First attempt with aiohttp for performance
        content = await self._fetch_text_content_aiohttp(user_store_url)
        if content:
            # Use BeautifulSoup to clean up HTML tags for AI readability
            soup = BeautifulSoup(content, 'html.parser')
            for script_or_style in soup(["script", "style"]): # Remove script and style tags
                script_or_style.decompose()
            text = await asyncio.to_thread(lambda: soup.get_text())
            # Break into lines and remove leading/trailing space on each.
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each.
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text_content = '\n'.join(chunk for chunk in chunks if chunk)
            return text_content[:15000] # Return first 15KB of cleaned text
        else:
            logger.warning(f"Could not fetch user store content with aiohttp, attempting Selenium for {user_store_url}")
            # Fallback to Selenium if aiohttp fails (e.g., for JS-rendered content)
            content = await self._fetch_html_content_selenium(user_store_url)
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                for script_or_style in soup(["script", "style"]):
                    script_or_style.decompose()
                text = await asyncio.to_thread(lambda: soup.get_text())
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text_content = '\n'.join(chunk for chunk in chunks if chunk)
                return text_content[:15000]
        return None

# --- Example Usage (for testing this script standalone) ---
async def main():
    import os # Added import
    from dotenv import load_dotenv # Added import
    load_dotenv() # Load .env for local testing

    scraper = GlobalEcommerceScraper()
    
    print("\n--- Scraping Amazon.com for 'Bluetooth headphones' ---")
    amazon_products = await scraper.scrape_marketplace_listings("Bluetooth headphones", marketplace_domain="amazon.com", max_products=5)
    print(f"Amazon Products: {amazon_products}")

    print("\n--- Scraping eBay.com for 'gaming mouse' ---")
    ebay_products = await scraper.scrape_marketplace_listings("gaming mouse", marketplace_domain="ebay.com", max_products=5)
    print(f"eBay Products: {ebay_products}")

    print("\n--- Scraping AliExpress for 'mini projector' ---")
    aliexpress_products = await scraper.scrape_marketplace_listings("mini projector", marketplace_domain="aliexpress.com", max_products=5)
    print(f"AliExpress Products: {aliexpress_products}")

    print("\n--- Scraping general content from a sample user store ---")
    sample_store_url = "https://www.shopify.com/examples/t-shirt-store" # Replace with a real, accessible URL for testing
    user_content = await scraper.get_user_store_content(sample_store_url)
    if user_content:
        print(f"Sample User Store Content (first 500 chars):\n{user_content[:500]}...")
    else:
        print("Failed to get user store content.")

if __name__ == "__main__":
    asyncio.run(main())
--- END OF FILE backend/global_ecommerce_scraper.py ---