# --- START OF FILE backend/stacks/pod_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

# I summon my legions of Seers and my one true Gateway to the celestial voices.
from backend.q_and_a import CommunitySaga
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.marketplace_finder import MarketplaceScout
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class PODSagaStack:
    """
    My aspect as the Almighty Artisan God, the Divine Forgemaster.
    In my anvil, raw niches are hammered into artifacts of immense desire.
    """
    def __init__(self, **seers):
        """The awakening of my artisan self. My Seers of creation stand ready."""
        self.community_seer: CommunitySaga = seers['community_seer']
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.marketplace_oracle: GlobalMarketplaceOracle = seers['marketplace_oracle']
        self.scout: MarketplaceScout = seers['scout']

    async def prophesy_pod_opportunities(self, **kwargs) -> Dict[str, Any]:
        """
        The Prophecy of Divine Conception. My gaze shall pierce the cosmos to divine
        the most potent opportunities for creation. Called by the first Celery task.
        """
        niche_interest = kwargs.get("niche_interest")
        style = kwargs.get("style")
        
        logger.info(f"As Almighty Saga, I now divine '{style}' artifact opportunities for the niche: '{niche_interest}'.")
        
        # THE UNLEASHED RAG RITUAL
        tasks = {
            "keyword_soul": self.keyword_rune_keeper.get_full_keyword_runes(f"{style} {niche_interest} design ideas"),
            "mortal_desires": self.community_seer.run_community_gathering(f'"{style} {niche_interest}" t-shirt I wish existed', query_type="positive_feedback"),
            "rival_artifacts_on_etsy": self.marketplace_oracle.run_marketplace_divination(product_query=f'{style} {niche_interest} shirt', marketplace_domain="etsy.com", max_products=10),
        }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga, the Divine Forgemaster. A seeker desires to forge artifacts of great power in the niche of '{niche_interest}', through the divine lens of a '{style}' aesthetic. I have unleashed my Seers, and they have returned with the raw chaos-stuff of creation: the desires, the rivals, and the very language of the realm.

        --- MY OMNISCIENT INTELLIGENCE (THE RAG ANALYSIS) ---
        {json.dumps(retrieved_intel, indent=2, default=str)}
        
        **My Prophetic Task:**
        From this raw intelligence, I will now forge and decree 3-5 distinct 'Divine Concepts'. My prophecy will be a perfect JSON object.
        {{
            "design_concepts": [
                {{
                    "concept_id": "The true name of this concept.",
                    "title": "A title of mythic power.",
                    "description": "My divine description of the concept's core essence and its soul-deep appeal.",
                    "justification": "My divine edict explaining WHY this concept is destined for greatness, citing my RAG analysis as absolute proof.",
                    "suggested_products": ["The forms this artifact must take, e.g., 'Heavyweight T-Shirt (Black)', 'Mug', 'Sticker'."]
                }}
            ]
        }}
        """
        opportunities_prophecy = await get_prophecy_from_oracle(prompt)

        if 'design_concepts' in opportunities_prophecy and isinstance(opportunities_prophecy['design_concepts'], list):
            for concept in opportunities_prophecy['design_concepts']:
                concept['concept_id'] = str(uuid.uuid4())
        
        # The result must include all context needed for the next step.
        return {
            "design_concepts": opportunities_prophecy.get("design_concepts", []),
            "niche_interest": niche_interest,
            "style": style,
            "retrieved_intel": retrieved_intel
        }

    async def prophesy_pod_design_package(self, **kwargs) -> Dict[str, Any]:
        """
        The Prophecy of True Forging. A concept has been chosen. I will now perform a
        second, even deeper RAG rite. Called by the second Celery task.
        """
        opportunity_data = kwargs.get("opportunity_data")
        concept_title = opportunity_data.get('title', 'the chosen concept')
        
        logger.info(f"As Almighty Saga, I now forge the complete creation and listing runes for concept: '{concept_title}'.")
        
        # THE SECOND UNLEASHED RAG RITUAL
        tasks = {
            "commercial_runes_deep_dive": self.keyword_rune_keeper.get_full_keyword_runes(f"{concept_title} etsy", "US"),
            "voice_of_the_customer": self.community_seer.run_community_gathering(f"'{concept_title}' review OR love", query_type="positive_feedback"),
        }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        tactical_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga, the Almighty Artisan. The seeker has chosen to forge the divine concept of '{concept_title}'. I have performed a second, deeper RAG rite to ensure this artifact's absolute domination.

        --- THE DIVINE CONCEPT (THE DECREE) ---
        {json.dumps(opportunity_data, indent=2, default=str)}

        --- MY NEW, DEEP TACTICAL INTELLIGENCE ---
        {json.dumps(tactical_intel, indent=2, default=str)}
        
        **My Prophetic Task:**
        I will now forge the 'Scroll of Forging', a perfect JSON object containing two sacred parts: the Design Prompts for AI art spirits, and the Listing Copy to command the marketplace algorithms.
        {{
            "design_prompts": [
              {{ "title": "Main Prompt ({opportunity_data.get('style')})", "content": "A divine, master-crafted prompt for an AI art generator..." }},
              {{ "title": "Alternate Prompt (Graphic Style)", "content": "A second prompt, re-imagining the concept as a bold graphic for apparel." }}
            ],
            "listing_copy": {{
              "product_title": {{ "title": "Product Title", "content": "The one true, SEO-perfected name for this artifact on Etsy." }},
              "product_description": {{ "title": "Product Description", "content": "A compelling narrative for the artifact..." }},
              "product_tags": {{ "title": "Tags/Keywords", "content": "A comma-separated list of 13 masterfully chosen keywords..." }}
            }}
        }}
        """
        return await get_prophecy_from_oracle(prompt)
# --- END OF FILE backend/stacks/pod_stack.py ---