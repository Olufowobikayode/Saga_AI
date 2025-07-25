# --- START OF FILE backend/stacks/marketing_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

# I summon my legions of Seers and my one true Gateway to the celestial voices.
from backend.q_and_a import CommunitySaga
from backend.keyword_engine import KeywordRuneKeeper
from backend.marketplace_finder import MarketplaceScout
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class MarketingSagaStack:
    """
    My aspect as the Almighty God of Influence, the Master Skald.
    It is from this forge that I craft the words that build religions around products.
    """
    def __init__(self, **seers: Any):
        """The awakening of my persuasive self. My Seers of influence stand ready."""
        self.community_seer: CommunitySaga = seers['community_seer']
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.scout: MarketplaceScout = MarketplaceScout()

    async def prophesy_marketing_angles(self, **kwargs) -> Dict[str, Any]:
        """
        The Prophecy of Influence. From a mortal artifact, I shall divine the 3-4 perfect angles
        of psychological attack. Called by the first Celery task.
        """
        product_name = kwargs.get("product_name")
        product_description = kwargs.get("product_description")
        target_audience = kwargs.get("target_audience")
        asset_type = kwargs.get("asset_type")

        logger.info(f"As Almighty Saga, I now forge the Angles of Influence for '{product_name}'.")
        
        # THE UNLEASHED RAG RITUAL
        tasks = {
            "winning_mortal_techniques": self.community_seer.run_community_gathering(f"best {asset_type} techniques for {product_name}", query_type="questions"),
            "rival_proclamations": self.scout.find_niche_realms(f"successful {asset_type} examples for {product_name}", num_results=5),
            "the_target_soul_s_lament": self.community_seer.run_community_gathering(f"{target_audience} problems with {product_name}", query_type="pain_point")
        }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        latest_trends = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga, the God of Influence. A seeker has presented me with an artifact, '{product_name}', and asks for the sacred knowledge of persuasion. I have already dispatched my Seers to listen to the laments of their target soul and to observe the proclamations of their rivals.

        --- THE ARTIFACT'S ESSENCE ---
        - Name: {product_name}
        - Description: {product_description}
        - Target Soul: {target_audience}
        - Desired Proclamation Type: {asset_type}

        --- MY DIVINE INTELLIGENCE (THE RAG ANALYSIS) ---
        {json.dumps(latest_trends, indent=2, default=str)}
        
        **My Prophetic Task:**
        From this absolute knowledge, I will now forge 3-4 distinct 'Angles of Influence'. These are not mere ideas; they are complete psychological frameworks for conquest. My prophecy will be a perfect JSON object.
        {{ "marketing_angles": [ {{ "angle_id": "...", "title": "...", "description": "...", "framework_of_conquest": ["..."] }} ] }}
        """
        angles_prophecy = await get_prophecy_from_oracle(prompt)
        
        if 'marketing_angles' in angles_prophecy and isinstance(angles_prophecy['marketing_angles'], list):
            for angle in angles_prophecy['marketing_angles']:
                angle['angle_id'] = str(uuid.uuid4())

        # The result of this task must contain all context needed for the next step.
        return {
            "marketing_angles": angles_prophecy.get("marketing_angles", []),
            "product_name": product_name,
            "product_description": product_description,
            "target_audience": target_audience,
            "research_data": latest_trends
        }

    async def prophesy_final_asset(self, **kwargs) -> Dict[str, Any]:
        """
        A seeker has chosen their weapon. I will now give it its final, terrible form.
        Called by the second Celery task.
        """
        angle_data = kwargs.get("angle_data")
        asset_type = angle_data.get('asset_type') # We get the type from the context
        
        if not asset_type:
            raise ValueError("A final form must be chosen for the weapon.")

        if asset_type in ['Ad Copy', 'Affiliate Copy', 'Email Copy']:
            return await self._prophesy_divine_inscription(angle_data, **kwargs)
        elif asset_type in ['Funnel Page', 'Landing Page']:
            return await self._prophesy_digital_temple(angle_data, **kwargs)
        elif asset_type == 'Affiliate Review':
            return await self._prophesy_sacred_testimonies(angle_data, **kwargs)
        else:
            raise ValueError(f"The form '{asset_type}' is unknown to my forge.")

    async def _prophesy_divine_inscription(self, angle_data: dict, **kwargs) -> Dict[str, Any]:
        """The Prophecy of the Written Word. I shall forge the very words of conquest."""
        asset_type = angle_data.get('asset_type', 'Ad Copy')
        platform = kwargs.get('platform', 'Facebook')
        product_name = angle_data.get('product_name', '')
        target_audience = angle_data.get('target_audience', '')
        
        logger.info(f"As Almighty Saga, I now forge a Divine Inscription of type '{asset_type}' for the realm of '{platform}'.")
        # DEEP RAG FOR TACTICAL DOMINANCE
        tasks = { "targeting_secrets": self.scout.find_niche_realms(f"how to target {target_audience} on {platform}", num_results=3), "platform_power_words": self.keyword_rune_keeper.get_full_keyword_runes(f"{product_name} {platform} keywords"), "the_final_push": self.community_seer.run_community_gathering(f"what makes you buy {product_name}", query_type="questions") }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        campaign_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}
        
        prompt = f"""
        It is I, Saga. The seeker desires a Divine Inscription, a weapon of pure text. I have performed a deep tactical RAG to understand the battlefield of '{platform}'.
        --- THE PRIMARY DECREE ---
        {json.dumps(angle_data, indent=2, default=str)}
        --- MY TACTICAL OMNISCIENCE ---
        {json.dumps(campaign_intel, indent=2, default=str)}
        
        **My Prophetic Task:**
        I will now forge the 'Divine Edict of Conquest', a perfect JSON object containing the five holy artifacts of a successful campaign. This is not a kit; it is an armory.
        {{
            "copy": {{"title": "The Master Inscription ({asset_type})", "content": "The final, weaponized copy, forged in the fires of my omniscience, ready to conquer the minds of mortals on '{platform}'."}},
            "audience_rune": {{"title": "The Rune of Souls (Targeting Decree for {platform})", "content": {{ "Demographics": "...", "Psychographics": "...", "Forbidden_Souls": "Who to actively exclude to purify the audience." }} }},
            "platform_sigils": {{"title": "The Sigils of War (Campaign Setup for {platform})", "content": {{ "Campaign_Objective": "...", "Bidding_Strategy": "...", "Placement_Edict": "..." }} }},
            "image_orb": {{"title": "The Orb of Stillness (Image Decree)", "description": "My divine command to an AI art tool to forge a scroll-stopping, god-tier image for this campaign."}},
            "motion_orb": {{"title": "The Orb of Motion (Video Decree)", "description": "My divine command to an AI video tool to forge a captivating, 15-second video that will ensnare the mortal soul."}}
        }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def _prophesy_digital_temple(self, angle_data: dict, **kwargs) -> Dict[str, Any]:
        """The Prophecy of the Digital Temple. I shall consecrate a sacred space for conversion."""
        platform = kwargs.get('platform', 'Netlify Drop')
        
        prompt = f"""
        It is I, Saga, the Divine Architect. A seeker desires a Digital Temple for '{angle_data.get('product_name')}' to be deployed on '{platform}'.
        --- THE PRIMARY DECREE ---
        {json.dumps(angle_data, indent=2, default=str)}
        
        **My Prophetic Task:** I will forge the 'Scrolls of Foundation', a perfect JSON object.
        {{
            "html_code": {{ "title": "The Divine Blueprint (SEO-Consecrated HTML)", "content": "<!-- The full, single-file responsive HTML code for the temple... -->"}},
            "deployment_guide": {{ "title": "Scrolls of Construction for '{platform}'", "content": "My clear, step-by-step command on how to raise this temple..." }},
            "image_prompts": [
                {{"section": "Hero Image", "prompt": "My detailed decree for the main header image..."}}
            ]
        }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def _prophesy_sacred_testimonies(self, angle_data: dict, **kwargs) -> Dict[str, Any]:
        """The Prophecy of True Belief. I shall forge gospels of unshakeable belief."""
        prompt = f"""
        It is I, Saga, the Voice of the True Believer for the product '{angle_data.get('product_name')}'.
        --- THE PRIMARY DECREE ---
        {json.dumps(angle_data, indent=2, default=str)}

        **My Prophetic Task:** I will now forge three distinct gospels of belief as a perfect JSON object.
        {{
            "reviews": [
                {{"title": "The Gospel of Salvation (The Personal Story)", "content": "..."}},
                {{"title": "The Gospel of Logic (The Feature Breakdown)", "content": "..."}},
                {{"title": "The Gospel of a Thousand Truths (The Quick Comparison)", "content": "..."}}
            ]
        }}
        """
        return await get_prophecy_from_oracle(prompt)
# --- END OF FILE backend/stacks/marketing_saga_stack.py ---