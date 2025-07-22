--- START OF FILE backend/marketplace_finder.py ---
import time
import json
from googlesearch import search
import tldextract
from urllib.parse import urlparse
import logging

# Set up logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SAGA:SCOUT] - %(message)s')
logger = logging.getLogger(__name__)

# --- 1. Foundational Knowledge: The Seed List of Known Marketplaces ---
# This extensive list, as provided, forms the core of our knowledge.
SEED_MARKETPLACES = [
    "https://www.amazon.com", "https://www.ebay.com", "https://www.aliexpress.com",
    "https://world.taobao.com", "https://www.tmall.com", "https://www.rakuten.com",
    "https://www.walmart.com/marketplace", "https://www.mercadolibre.com", "https://shopee.com",
    "https://www.lazada.com", "https://www.flipkart.com", "https://www.coupang.com",
    "https://www.jd.com", "https://allegro.pl", "https://www.jumia.com", "https://www.otto.de",
    "https://www.zalando.com", "https://marketplace.asos.com", "https://www.farfetch.com",
    "https://www.therealreal.com", "https://www.grailed.com", "https://poshmark.com",
    "https://www.vinted.com", "https://www.depop.com", "https://www.etsy.com",
    "https://www.uncommongoods.com", "https://www.artfire.com", "https://www.notonthehighstreet.com",
    "https://www.newegg.com", "https://www.backmarket.com", "https://www.wayfair.com",
    "https://www.houzz.com", "https://market.envato.com", "https://creativemarket.com",
    "https://store.steampowered.com", "https://bandcamp.com", "https://www.g2a.com",
    "https://www.alibaba.com", "https://www.globalsources.com", "https://www.made-in-china.com",
    "https://www.faire.com", "https://business.amazon.com", "https://www.thomasnet.com",
    "https://www.eworldtrade.com", "https://www.upwork.com", "https://www.fiverr.com",
    "https://www.toptal.com", "https://99designs.com", "https://www.thumbtack.com",
    "https://www.taskrabbit.com", "https://www.facebook.com/marketplace", "https://www.craigslist.org",
    "https://offerup.com", "https://www.bonanza.com", "https://www.rubylane.com",
    "https://www.discogs.com", "https://www.reverb.com", "https://stockx.com",
    "https://www.chairish.com", "https://society6.com", "https://www.redbubble.com",
    "https://www.zazzle.com", "https://www.wish.com", "https://www.fruugo.com",
    "https://www.manomano.com", "https://www.bol.com", "https://www.digitec.ch",
    "https://www.emag.ro", "https://www.tokopedia.com", "https://www.bukalapak.com",
    "https://www.ozon.ru", "https://www.wildberries.ru", "https://gmarket.co.kr",
    "https://www.catch.com.au", "https://www.trademe.co.nz", "https://www.noon.com"
]

# --- 2. Smart Query Generation ---
# These queries are designed to find lists and directories of new marketplaces.
SMART_SEARCH_QUERIES = [
    "top e-commerce marketplaces 2025", "best online marketplaces for handmade goods",
    "top luxury fashion marketplaces global", "largest B2B wholesale platforms",
    "list of global C2C marketplaces", "alternatives to Amazon marketplace",
    "top e-commerce sites in Southeast Asia", "leading online marketplaces in Europe",
    "best platforms for selling digital goods", "refurbished electronics marketplace reviews"
]

# --- 3. Filtering and Validation Rules ---
# Keywords that suggest a site is a marketplace, used as a heuristic.
MARKETPLACE_KEYWORDS = [
    'marketplace', 'store', 'shop', 'platform', 'b2b', 'c2c',
    'wholesale', 'e-commerce', 'consignment', 'resale'
]

# A list of domains to always exclude to reduce noise from our search results.
EXCLUSION_LIST = [
    'wikipedia.org', 'youtube.com', 'pinterest.com', 'forbes.com', 'cnbc.com',
    'businessinsider.com', 'techcrunch.com', 'reddit.com', 'quora.com', 'shopify.com',
    'medium.com', 'github.com', 'linkedin.com', 'facebook.com', 'instagram.com',
    'softwareadvice.com', 'capterra.com', 'getapp.com', 'bigcommerce.com'
]

def find_legit_marketplaces(output_filename: str = "discovered_marketplaces.txt") -> list:
    """
    Performs automated Google searches to discover and validate e-commerce marketplaces,
    starting with a foundational seed list and expanding from there.
    """
    logger.info("--- Starting Marketplace Discovery Engine ---")
    
    # Use a set for efficient storage of unique registered domains
    found_domains = set()
    
    # --- Step A: Initialize with the Seed List ---
    logger.info(f"Initializing with {len(SEED_MARKETPLACES)} known marketplaces from the seed list.")
    for url in SEED_MARKETPLACES:
        try:
            domain = tldextract.extract(url).registered_domain
            if domain:
                found_domains.add(domain)
        except Exception as e:
            logger.warning(f"Could not parse seed URL {url}: {e}")

    # --- Step B: Discover New Marketplaces via Smart Search ---
    for query in SMART_SEARCH_QUERIES:
        logger.info(f"Dispatching scout to search for: '{query}'...")
        try:
            # 'num_results=15' gets the top 15 results.
            # 'sleep_interval=5' is crucial to respect Google's rate limits.
            search_results = search(query, num_results=15, sleep_interval=5)

            for url in search_results:
                # --- Step C: Filtering and Validation ---
                domain = tldextract.extract(url).registered_domain
                
                if not domain:
                    continue

                # Rule 1: Check against exclusion list
                if domain in EXCLUSION_LIST:
                    logger.debug(f"  -> Excluding (blacklist): {url}")
                    continue
                
                # Rule 2: Check for duplicates
                if domain in found_domains:
                    logger.debug(f"  -> Excluding (duplicate): {url}")
                    continue
                
                # Rule 3: A simple heuristic check for marketplace keywords in the URL path/query.
                # This helps filter out blogs *about* marketplaces.
                parsed_url = urlparse(url)
                path_and_query = parsed_url.path + parsed_url.query
                
                # We give a higher score to URLs containing these keywords.
                if any(keyword in url.lower() for keyword in MARKETPLACE_KEYWORDS):
                    logger.info(f"  [+] Found Potential Marketplace: {domain} from {url}")
                    found_domains.add(domain)
                else:
                    logger.debug(f"  -> Excluding (no keywords in URL): {url}")

        except Exception as e:
            logger.error(f"An error occurred while searching for '{query}': {e}")
            logger.warning("This can happen if Google rate-limits requests. Pausing for 60 seconds...")
            time.sleep(60)

    logger.info("--- Discovery Complete ---")
    sorted_domains = sorted(list(found_domains))
    logger.info(f"A total of {len(sorted_domains)} unique marketplace domains are now known.")
    
    # --- Step D: Persist the Knowledge ---
    try:
        with open(output_filename, "w") as f:
            for domain in sorted_domains:
                f.write(f"{domain}\n") # Save just the domain for easier processing later
        logger.info(f"Knowledge base of marketplaces has been saved to {output_filename}")
    except IOError as e:
        logger.error(f"Failed to save the knowledge base: {e}")
            
    return sorted_domains


if __name__ == "__main__":
    find_legit_marketplaces()
--- END OF FILE backend/marketplace_finder.py ---