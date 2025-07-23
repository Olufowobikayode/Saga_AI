import time
import json
import logging
from urllib.parse import urlparse
import tldextract
from typing import List, Set, Literal

# ### ENHANCEMENT: Import multiple search libraries for resilience
from googlesearch import search as google_search
from duckduckgo_search import DDGS

from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SAGA:SCOUT] - %(message)s')
logger = logging.getLogger(__name__)

SearchEngine = Literal["duckduckgo", "google"]

class MarketplaceScout:
    """
    Saga's multi-engine scout, tasked with discovering realms of commerce and knowledge.
    It primarily uses DuckDuckGo for reliability and can use Google for deep dives,
    making it resilient and versatile.
    """
    def __init__(self):
        self.found_domains: Set[str] = set()
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

        # --- Foundational Knowledge: The Seed List of Known Marketplaces ---
        self.SEED_MARKETPLACES: List[str] = [
            "https://www.amazon.com", "https://www.ebay.com", "https://www.aliexpress.com", "https://www.etsy.com",
            "https://www.walmart.com/marketplace", "https://www.rakuten.com", "https://world.taobao.com",
            "https://www.alibaba.com", "https://www.mercadolibre.com", "https://shopee.com", "https://www.lazada.com",
        ]

        # --- Smart Query Generation ---
        self.GENERAL_SEARCH_QUERIES: List[str] = [
            "top e-commerce marketplaces 2025", "largest online shopping platforms global",
            "list of global c2c marketplaces", "alternatives to Amazon marketplace",
        ]

        self.NICHE_SEARCH_QUERIES_TEMPLATE: str = 'best marketplaces for selling {niche}'
        self.BEST_PRODUCTS_QUERIES_TEMPLATE: str = 'best {interest} products of 2025'
        self.QA_SITE_QUERIES_TEMPLATE: str = 'top q&a sites for {interest}'
        
        # --- Filtering and Validation Rules ---
        self.EXCLUSION_LIST: List[str] = [
            'wikipedia.org', 'youtube.com', 'pinterest.com', 'forbes.com', 'cnbc.com', 'businessinsider.com',
            'techcrunch.com', 'reddit.com', 'quora.com', 'stackoverflow.com', 'github.com', 'shopify.com',
        ]

    def _search(self, query: str, num_results: int = 10, engine: SearchEngine = "duckduckgo") -> List[str]:
        """A master search method that can delegate to different search engines."""
        logger.info(f"Scout is searching for: '{query}' using {engine.capitalize()}...")
        try:
            if engine == "duckduckgo":
                # DuckDuckGo is more reliable and less likely to block
                with DDGS() as ddgs:
                    results = [r['href'] for r in ddgs.text(query, max_results=num_results)]
                return results
            
            elif engine == "google":
                # Google gives high-quality results but is prone to blocking
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
            # Skip non-http links which can appear in results
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
            # Use the most reliable engine for general discovery
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
        Performs a focused, resilient search for niche-specific realms.
        It tries the reliable engine first, then falls back to the deep-dive engine.
        """
        logger.info(f"--- Scout commencing mission: Discover Niche Realms for '{topic}' ---")
        
        queries = [
            self.NICHE_SEARCH_QUERIES_TEMPLATE.format(niche=topic),
            self.BEST_PRODUCTS_QUERIES_TEMPLATE.format(interest=topic),
            self.QA_SITE_QUERIES_TEMPLATE.format(interest=topic)
        ]
        
        all_urls = set()

        for query in queries:
            # 1. Try with the fast, reliable engine first
            results = self._search(query, num_results=num_results, engine="duckduckgo")
            
            # 2. If it fails or returns too few results, use the deep-dive engine as a fallback
            if len(results) < num_results / 2:
                logger.warning(f"DuckDuckGo returned few results for '{query}'. Falling back to Google for a deep dive.")
                time.sleep(2) # Be respectful between engine switches
                google_results = self._search(query, num_results=num_results, engine="google")
                results.extend(google_results)

            for url in results:
                all_urls.add(url)

        logger.info(f"Scout has returned with {len(all_urls)} potential niche realms for '{topic}'.")
        return list(all_urls)

# Standalone execution for testing
if __name__ == "__main__":
    scout = MarketplaceScout()
    
    print("\n--- Testing Niche Discovery with Multi-Engine Fallback ---")
    niche_realms = scout.find_niche_realms("fountain pen restoration")
    print("Found potential niche realms:")
    for i, realm in enumerate(niche_realms):
        if i >= 15: break # Print top 15 for brevity
        print(f"- {realm}")