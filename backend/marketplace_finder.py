import time
import json
import logging
from urllib.parse import urlparse
import tldextract
from typing import List, Set, Literal

from googlesearch import search as google_search
from duckduckgo_search import DDGS
from fake_useragent import UserAgent

# ### FIX: Import the caching utilities
from backend.cache import seer_cache, generate_cache_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SAGA:SCOUT] - %(message)s')
logger = logging.getLogger(__name__)

SearchEngine = Literal["duckduckgo", "google"]

class MarketplaceScout:
    """
    Saga's multi-engine scout, tasked with discovering realms of commerce and knowledge.
    It primarily uses DuckDuckGo for reliability and can use Google for deep dives,
    making it resilient and versatile. It now uses a cache to avoid repeated searches.
    """
    def __init__(self):
        self.found_domains: Set[str] = set()
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

        self.SEED_MARKETPLACES: List[str] = [
            "https://www.amazon.com", "https://www.ebay.com", "https://www.aliexpress.com", "https://www.etsy.com",
            "https://www.walmart.com/marketplace", "https://www.rakuten.com", "https://world.taobao.com",
            "https://www.alibaba.com", "https://www.mercadolibre.com", "https://shopee.com", "https://www.lazada.com",
        ]

        self.GENERAL_SEARCH_QUERIES: List[str] = [
            "top e-commerce marketplaces 2025", "largest online shopping platforms global",
            "list of global c2c marketplaces", "alternatives to Amazon marketplace",
        ]

        self.NICHE_SEARCH_QUERIES_TEMPLATE: str = 'best marketplaces for selling {niche}'
        self.BEST_PRODUCTS_QUERIES_TEMPLATE: str = 'best {interest} products of 2025'
        self.QA_SITE_QUERIES_TEMPLATE: str = 'top q&a sites for {interest}'
        
        self.EXCLUSION_LIST: List[str] = [
            'wikipedia.org', 'youtube.com', 'pinterest.com', 'forbes.com', 'cnbc.com', 'businessinsider.com',
            'techcrunch.com', 'reddit.com', 'quora.com', 'stackoverflow.com', 'github.com', 'shopify.com',
        ]

    def _search(self, query: str, num_results: int = 10, engine: SearchEngine = "duckduckgo") -> List[str]:
        """A master search method that can delegate to different search engines."""
        logger.info(f"Scout is searching for: '{query}' using {engine.capitalize()}...")
        try:
            if engine == "duckduckgo":
                with DDGS() as ddgs:
                    results = [r['href'] for r in ddgs.text(query, max_results=num_results)]
                return results
            
            elif engine == "google":
                user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
                return list(google_search(query, num_results=num_results, stop=num_results, pause=3.0, user_agent=user_agent))

        except Exception as e:
            logger.error(f"The scout was halted while searching '{query}' with {engine}: {e}")
            if "HTTP Error 429" in str(e):
                logger.warning(f"{engine.capitalize()}'s guardians have noticed our presence. Pausing...")
                time.sleep(180)
        return []

    def _validate_and_add_domain(self, url: str) -> None:
        """Parses a URL, validates it, and adds the domain to the found list if it's new and valid."""
        try:
            if not url.startswith(('http://', 'https://')):
                return
            domain = tldextract.extract(url).registered_domain
            if not domain or domain in self.EXCLUSION_LIST or domain in self.found_domains:
                return
            
            logger.info(f"  [+] Scout discovered a new potential realm: {domain} from {url}")
            self.found_domains.add(domain)

        except Exception as e:
            logger.warning(f"Could not parse or validate URL {url}: {e}")

    def find_general_marketplaces(self, output_filename: str = "discovered_marketplaces.txt") -> List[str]:
        """Discovers general e-commerce marketplaces using the primary, reliable engine."""
        logger.info("--- Scout commencing mission: Discover General Marketplaces ---")
        self.found_domains = {tldextract.extract(url).registered_domain for url in self.SEED_MARKETPLACES}
        
        for query in self.GENERAL_SEARCH_QUERIES:
            results = self._search(query, engine="duckduckgo")
            for url in results:
                self._validate_and_add_domain(url)
        
        sorted_domains = sorted(list(self.found_domains))
        try:
            with open(output_filename, "w") as f:
                for domain in sorted_domains:
                    f.write(f"{domain}\n")
            logger.info(f"Knowledge base of {len(sorted_domains)} general marketplaces has been updated in {output_filename}")
        except IOError as e:
            logger.error(f"Failed to save the knowledge base: {e}")
        return sorted_domains

    def find_niche_realms(self, topic: str, num_results: int = 10) -> List[str]:
        """
        Performs a focused, resilient, and cached search for niche-specific realms.
        """
        # ### ENHANCEMENT: Implement caching for this expensive operation.
        cache_key = generate_cache_key("find_niche_realms", topic=topic, num_results=num_results)
        cached_results = seer_cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        logger.info(f"--- Scout commencing mission: Discover Niche Realms for '{topic}' ---")
        
        queries = [
            self.NICHE_SEARCH_QUERIES_TEMPLATE.format(niche=topic),
            self.BEST_PRODUCTS_QUERIES_TEMPLATE.format(interest=topic),
            self.QA_SITE_QUERIES_TEMPLATE.format(interest=topic)
        ]
        
        all_urls = set()

        for query in queries:
            results = self._search(query, num_results=num_results, engine="duckduckgo")
            
            if len(results) < num_results / 2:
                logger.warning(f"DuckDuckGo returned few results for '{query}'. Falling back to Google for a deep dive.")
                time.sleep(2)
                google_results = self._search(query, num_results=num_results, engine="google")
                results.extend(google_results)

            for url in results:
                all_urls.add(url)

        final_results = list(all_urls)
        logger.info(f"Scout has returned with {len(final_results)} potential niche realms for '{topic}'.")
        
        # ### ENHANCEMENT: Set the result in the cache with a long TTL (1 day = 86400 seconds).
        seer_cache.set(cache_key, final_results, ttl_seconds=86400)
        
        return final_results

# Standalone execution for testing
if __name__ == "__main__":
    scout = MarketplaceScout()
    
    print("\n--- Testing Niche Discovery with Caching ---")
    start_time = time.time()
    print("--- First Call (should be slow) ---")
    niche_realms_1 = scout.find_niche_realms("fountain pen restoration")
    duration_1 = time.time() - start_time
    print(f"Found {len(niche_realms_1)} realms in {duration_1:.2f} seconds.")

    start_time_2 = time.time()
    print("\n--- Second Call (should be instant) ---")
    niche_realms_2 = scout.find_niche_realms("fountain pen restoration")
    duration_2 = time.time() - start_time_2
    print(f"Found {len(niche_realms_2)} realms in {duration_2:.4f} seconds.")

    if duration_2 < 0.1 and len(niche_realms_1) == len(niche_realms_2):
        print("\n[SUCCESS] Caching is working as expected!")
    else:
        print("\n[FAILURE] Caching is not working correctly.")