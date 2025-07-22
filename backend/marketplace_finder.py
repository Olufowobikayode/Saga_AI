--- START OF FILE backend/marketplace_finder.py ---
import time
import json
import logging
from urllib.parse import urlparse
import tldextract
from googlesearch import search
from typing import List, Dict, Set

# Set up logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SAGA:SCOUT] - %(message)s')
logger = logging.getLogger(__name__)

# --- Foundational Knowledge & Search Queries are now combined into a more powerful class ---

class MarketplaceScout:
    """
    Saga's scout, tasked with discovering new realms of commerce and knowledge across the web.
    Its capabilities have been expanded to find general marketplaces, niche-specific havens,
    and lists of the finest artifacts.
    """
    def __init__(self):
        self.found_domains: Set[str] = set()
        
        # --- 1. Foundational Knowledge: The Seed List of Known Marketplaces ---
        self.SEED_MARKETPLACES: List[str] = [
            "https://www.amazon.com", "https://www.ebay.com", "https://www.aliexpress.com", "https://www.etsy.com",
            "https://www.walmart.com/marketplace", "https://www.rakuten.com", "https://world.taobao.com",
            "https://www.alibaba.com", "https://www.mercadolibre.com", "https://shopee.com", "https://www.lazada.com",
            "https://www.flipkart.com", "https://allegro.pl", "https://www.zalando.com", "https://www.newegg.com",
            "https://www.wayfair.com", "https://www.facebook.com/marketplace", "https://www.craigslist.org"
            # A more focused seed list for clarity
        ]

        # --- 2. Smart Query Generation ---
        self.GENERAL_SEARCH_QUERIES: List[str] = [
            "top e-commerce marketplaces 2025", "largest online shopping platforms global",
            "list of global c2c marketplaces", "alternatives to Amazon marketplace",
            "leading online marketplaces in Europe", "top e-commerce sites in Southeast Asia"
        ]

        # --- NEW: Queries for Niche and "Best Of" Discovery ---
        self.NICHE_SEARCH_QUERIES_TEMPLATE: str = 'best marketplaces for selling {niche}'
        self.BEST_PRODUCTS_QUERIES_TEMPLATE: str = 'best {interest} products of 2025'
        self.QA_SITE_QUERIES_TEMPLATE: str = 'top q&a sites for {interest}'
        
        # --- 3. Filtering and Validation Rules ---
        self.EXCLUSION_LIST: List[str] = [
            'wikipedia.org', 'youtube.com', 'pinterest.com', 'forbes.com', 'cnbc.com', 'businessinsider.com',
            'techcrunch.com', 'reddit.com', 'quora.com', 'stackoverflow.com', 'github.com', 'shopify.com',
            'medium.com', 'linkedin.com', 'facebook.com', 'instagram.com', 'twitter.com', 'tiktok.com',
            'softwareadvice.com', 'capterra.com', 'getapp.com', 'bigcommerce.com', 'wix.com', 'squarespace.com'
        ]

    def _search_google(self, query: str, num_results: int = 10) -> List[str]:
        """A more robust and patient method for searching, with better error handling."""
        logger.info(f"Scout is searching for: '{query}'...")
        try:
            return list(search(query, num=num_results, stop=num_results, pause=3.0))
        except Exception as e:
            logger.error(f"The scout was halted while searching for '{query}': {e}")
            if "HTTP Error 429" in str(e):
                logger.warning("Google's guardians have noticed our presence. Pausing for 3 minutes...")
                time.sleep(180)
            else:
                logger.warning("An unknown obstacle was encountered. Pausing for 30 seconds...")
                time.sleep(30)
        return []

    def _validate_and_add_domain(self, url: str) -> None:
        """Parses a URL, validates it, and adds the domain to the found list if it's new and valid."""
        try:
            domain = tldextract.extract(url).registered_domain
            if not domain or domain in self.EXCLUSION_LIST or domain in self.found_domains:
                return
            
            logger.info(f"  [+] Scout discovered a new potential realm: {domain} from {url}")
            self.found_domains.add(domain)

        except Exception as e:
            logger.warning(f"Could not parse or validate URL {url}: {e}")

    def find_general_marketplaces(self, output_filename: str = "discovered_marketplaces.txt") -> List[str]:
        """Discovers general e-commerce marketplaces."""
        logger.info("--- Scout commencing mission: Discover General Marketplaces ---")
        self.found_domains = {tldextract.extract(url).registered_domain for url in self.SEED_MARKETPLACES}
        
        for query in self.GENERAL_SEARCH_QUERIES:
            results = self._search_google(query)
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
        Performs a focused search for niche-specific marketplaces or communities.
        Returns a list of URLs.
        """
        logger.info(f"--- Scout commencing mission: Discover Niche Realms for '{topic}' ---")
        urls = []
        
        # Search for niche marketplaces
        niche_query = self.NICHE_SEARCH_QUERIES_TEMPLATE.format(niche=topic)
        urls.extend(self._search_google(niche_query, num_results))
        
        # Search for "best of" lists which often contain product links
        best_of_query = self.BEST_PRODUCTS_QUERIES_TEMPLATE.format(interest=topic)
        urls.extend(self._search_google(best_of_query, num_results))

        # Search for Q&A sites related to the topic
        qa_query = self.QA_SITE_QUERIES_TEMPLATE.format(interest=topic)
        urls.extend(self._search_google(qa_query, num_results))

        logger.info(f"Scout has returned with {len(urls)} potential niche realms for '{topic}'.")
        return list(set(urls)) # Return unique URLs

# Standalone execution for general marketplace discovery
if __name__ == "__main__":
    scout = MarketplaceScout()
    scout.find_general_marketplaces()

    # Example of how the new functions would be used
    print("\n--- Testing Niche Discovery ---")
    niche_realms = scout.find_niche_realms("handmade leather goods")
    print("Found potential niche realms:")
    for realm in niche_realms[:5]: # Print top 5 for brevity
        print(f"- {realm}")
--- END OF FILE backend/marketplace_finder.py ---