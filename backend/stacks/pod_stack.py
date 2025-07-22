--- START OF FILE backend/stacks/pod_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

import google.generativeai as genai

# --- Import Saga's Seers and Oracles ---
from backend.q_and_a import CommunitySaga
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.marketplace_finder import MarketplaceScout
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class PODSagaStack:
    """
    Saga's aspect as the Muse of Artisans. This stack navigates the world of
    Print on Demand by identifying trending niche opportunities and generating
    both AI design prompts and the sales copy needed to list the final product.
    """
    def __init__(self, model: genai.GenerativeModel, **seers):
        """Initializes the stack with the AI oracle and all necessary seers."""
        self.model = model
        self.community_seer: CommunitySaga = seers['community_seer']
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.marketplace_oracle: GlobalMarketplaceOracle = seers['marketplace_oracle']
        self.scout: MarketplaceScout = MarketplaceScout()

    async def prophesy_pod_opportunities(self, niche_interest: str) -> Dict[str, Any]:
        """
        Phase 1: Performs deep research on a niche to identify the most
        promising design concepts and opportunities.
        """
        logger.info(f"POD SAGA (PHASE 1): Divining opportunities for niche: '{niche_interest}'...")

        tasks = {
            "keyword_trends": self.keyword_rune_keeper.get_full_keyword_runes(niche_interest),
            "community_desires": self.community_seer.run_community_gathering(f'{niche_interest} t-shirt ideas', query_type="questions"),
            "top_selling_designs": self.marketplace_oracle.divine_marketplace_sagas(product_query=f'{niche_interest} shirt', marketplace_domain="etsy.com", max_products=5),
            "pod_platform_suggestions": self.scout.find_niche_realms(f"print on demand for {niche_interest}", num_results=3)
        }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        You are Saga, the Muse of Artisans. A creator seeks to conquer the Print on Demand (POD) realm for the niche: '{niche_interest}'. You have gathered intelligence on what is popular and desired right now.

        --- GATHERED INTELLIGENCE ---
        **Keyword Trends (What people are searching for):** {json.dumps(retrieved_intel.get('keyword_trends'), indent=2, default=str)}
        **Community Desires (What fans are asking for):** {json.dumps(retrieved_intel.get('community_desires'), indent=2, default=str)}
        **Top Selling Designs on Etsy (What is actually selling):** {json.dumps(retrieved_intel.get('top_selling_designs'), indent=2, default=str)}
        **Suggested POD Platforms (Where to sell):** {json.dumps(retrieved_intel.get('pod_platform_suggestions'), indent=2, default=str)}
        --- END INTELLIGENCE ---

        **Your Prophetic Task:**
        Synthesize all this intelligence to create 3-5 distinct "Design Concept Cards." These are strategic opportunities.

        Your output MUST be a valid JSON object with a single key, "design_concepts". Each concept card must contain:
        - "concept_id": A unique identifier.
        - "title": A catchy name for the design concept (e.g., "Retro-Futurist Catstronaut," "Minimalist Geometric Wolf").
        - "description": A brief explanation of the concept and its appeal.
        - "justification": Explain WHY this is a good idea by explicitly referencing the gathered intelligence.
        - "suggested_products": An array of product types this design would excel on (e.g., ["T-Shirt (dark colors)", "Mug", "Sticker"]).
        """
        opportunities_prophecy = await get_prophecy_from_oracle(self.model, prompt)
        
        if 'design_concepts' in opportunities_prophecy and isinstance(opportunities_prophecy['design_concepts'], list):
            for concept in opportunities_prophecy['design_concepts']:
                concept['concept_id'] = str(uuid.uuid4())
        
        opportunities_prophecy['niche_interest'] = niche_interest
        opportunities_prophecy['retrieved_intel'] = retrieved_intel
        
        return opportunities_prophecy

    async def prophesy_pod_design_package(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: Takes a chosen Design Concept and generates a complete creation AND listing package.
        """
        concept_title = opportunity_data.get('title', 'the chosen concept')
        logger.info(f"POD SAGA (PHASE 2): Weaving creation & listing runes for concept: '{concept_title}'...")

        prompt = f"""
        You are an expert prompt engineer for AI image generators AND a master e-commerce copywriter for Print on Demand platforms like Etsy and Redbubble. Your task is to generate a COMPLETE package for a creator: both the AI art prompts and the sales copy to sell the resulting design.

        --- STRATEGIC DESIGN CONCEPT (Your Command) ---
        - Title: {concept_title}
        - Description: {opportunity_data.get('description')}
        - Justification: {opportunity_data.get('justification')}
        - Suggested Products: {json.dumps(opportunity_data.get('suggested_products'), indent=2)}

        --- ORIGINAL RESEARCH (For Context on Keywords and Style) ---
        {json.dumps(opportunity_data.get('retrieved_intel', {}), indent=2, default=str)}

        **Your Prophetic Task:**
        Generate a complete package with two parts: The Design Prompts and The Listing Copy.

        Your output MUST be a valid JSON object structured for a user to easily copy each part:
        {{
            "design_prompts": [
              {{
                "title": "Style: Vintage Cartoon",
                "content": "A highly detailed prompt for a vintage cartoon style design... --ar 2:3"
              }},
              {{
                "title": "Style: Photorealistic",
                "content": "A highly detailed prompt for a photorealistic style design... --ar 2:3"
              }},
              {{
                "title": "Style: Minimalist Line Art",
                "content": "A highly detailed prompt for a minimalist line art style design... --ar 2:3"
              }}
            ],
            "listing_copy": {{
              "product_title": {{
                "title": "Product Title",
                "content": "A catchy, SEO-friendly title for an Etsy or Redbubble listing, including keywords from the research."
              }},
              "product_description": {{
                "title": "Product Description",
                "content": "A compelling, paragraph-based description of the product (e.g., t-shirt). It should tell a story about the design and mention the quality of the print and material."
              }},
              "product_tags": {{
                "title": "Product Tags / Keywords",
                "content": "A comma-separated list of 10-15 highly relevant keywords for the design, perfect for the tags section on a POD platform. Use the keyword research."
              }}
            }}
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

--- END OF FILE backend/stacks/pod_stack.py ---