# --- START OF FILE backend/stacks/marketing_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional

import google.generativeai as genai

from backend.q_and_a import CommunitySaga
from backend.keyword_engine import KeywordRuneKeeper
from backend.marketplace_finder import MarketplaceScout
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class MarketingSagaStack:
    """
    Saga's most powerful aspect for persuasion. This stack translates strategic goals
    into complete, data-driven "Campaign Deployment Kits" designed for maximum conversion
    and SEO dominance.
    """
    def __init__(self, model: genai.GenerativeModel, **seers: Any):
        self.model = model
        self.community_seer: CommunitySaga = seers['community_seer']
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.scout: MarketplaceScout = MarketplaceScout()

    async def prophesy_marketing_angles(self, product_name: str, product_description: str, target_audience: str, asset_type: str) -> Dict[str, Any]:
        logger.info(f"MARKETING SAGA (PHASE 1): Forging marketing angles for '{product_name}'...")
        tasks = {
            "best_techniques": self.community_seer.run_community_gathering(f"best {asset_type} techniques for {product_name} 2025", query_type="questions"),
            "competitor_examples": self.scout.find_niche_realms(f"successful {asset_type} examples for {product_name}", num_results=5),
            "audience_pain_points": self.community_seer.run_community_gathering(f"{target_audience} problems with {product_name}", query_type="pain_point")
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        latest_trends = {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}

        prompt = f"""
        You are Saga, a master marketing strategist. Create several strategic "angles" based on deep market research.
        --- PRODUCT INTEL ---
        - Product Name: {product_name}
        - Description: {product_description}
        - Target Audience: {target_audience}
        - Asset to Create: {asset_type}
        --- FRESH RESEARCH ---
        {json.dumps(latest_trends, indent=2, default=str)}
        --- END RESEARCH ---
        **Your Prophetic Task:**
        Based on your research, generate 3-4 distinct, actionable "Marketing Angle Cards."
        Your output MUST be a valid JSON object with a single key, "marketing_angles", which is an array of objects, each with:
        - "angle_id": A unique identifier.
        - "title": A compelling name for this marketing strategy (e.g., "The 'Us vs. Them' Manifesto").
        - "description": A short explanation of the psychological principle behind this angle.
        - "framework_steps": An array of steps outlining how to execute this angle.
        """
        angles_prophecy = await get_prophecy_from_oracle(self.model, prompt)
        if 'marketing_angles' in angles_prophecy and isinstance(angles_prophecy['marketing_angles'], list):
            for angle in angles_prophecy['marketing_angles']:
                angle['angle_id'] = str(uuid.uuid4())
        
        angles_prophecy.update({
            'product_name': product_name,
            'product_description': product_description,
            'target_audience': target_audience,
            'research_data': latest_trends
        })
        return angles_prophecy

    # --- THIS IS THE NEW, UNIFIED METHOD FOR ALL FINAL ASSET GENERATION ---
    async def prophesy_final_asset(self, angle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        A unified function to generate any final asset. It routes to the correct
        prompt and RAG ritual based on the 'asset_type' provided in the angle_data.
        """
        asset_type = angle_data.get('asset_type')
        if not asset_type:
            raise ValueError("Asset type must be provided to generate a final asset.")

        if asset_type in ['Ad Copy', 'Affiliate Copy', 'Email Copy']:
            return await self._prophesy_campaign_kit(angle_data)
        elif asset_type in ['Funnel Page', 'Landing Page']:
            return await self._prophesy_html_page(angle_data)
        elif asset_type == 'Affiliate Review':
            return await self._prophesy_affiliate_review(angle_data)
        else:
            raise ValueError(f"Unknown asset type '{asset_type}' for final prophecy.")

    async def _prophesy_campaign_kit(self, angle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates the 5-fold "Campaign Deployment Kit" for text assets."""
        asset_type = angle_data.get('asset_type', 'Ad Copy')
        platform = angle_data.get('platform', 'Facebook')
        product_name = angle_data.get('product_name', '')
        target_audience = angle_data.get('target_audience', '')
        logger.info(f"FORGING CAMPAIGN KIT: Type='{asset_type}', Platform='{platform}'")

        # DEEP-DIVE RAG
        tasks = {
            "targeting_guides": self.scout.find_niche_realms(f"how to target {target_audience} on {platform}", num_results=3),
            "platform_keywords": self.keyword_rune_keeper.get_full_keyword_runes(f"{product_name} {platform} keywords"),
            "conversion_drivers": self.community_seer.run_community_gathering(f"what makes you buy {product_name}", query_type="questions")
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        campaign_intel = {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}
        
        # FINAL, UPGRADED PROMPT
        prompt = f"""
        You are a world-class performance marketer and media buyer, tasked with creating a complete "Campaign Deployment Kit" for a specific platform. Your goal is 100% conversion. Every part of your prophecy must be sharp, actionable, and based on the provided intelligence.

        --- PRIMARY INTEL ---
        - Product: {product_name}
        - Target Audience: {target_audience}
        - Target Platform: {platform}
        - Strategic Angle: {json.dumps(angle_data.get('angle_id'), indent=2)}
        --- DEEP-DIVE INTELLIGENCE ---
        {json.dumps(campaign_intel, indent=2, default=str)}
        
        **Your Prophetic Task:**
        Generate the 5-fold prophecy. Your output MUST be a valid JSON object structured EXACTLY as follows:
        {{
            "copy": {{"title": "The Scribe's Scroll ({asset_type})", "content": "The masterfully crafted, high-conversion copy, precisely following the strategic angle and tailored for {platform}."}},
            "audience_rune": {{
                "title": "The Audience Rune (Targeting for {platform})", 
                "content": {{
                    "Demographics": "e.g., Age: 25-40, Gender: Both", "Location": "e.g., USA, Canada, UK urban centers",
                    "Interests_Behaviors": ["e.g., tech enthusiasts, online shoppers"], "Psychographics": "e.g., Values quality, seeks efficiency."
                }}
            }},
            "platform_sigils": {{
                "title": "The Scribe's Sigils (Setup for {platform})",
                "content": {{
                    "Campaign_Objective": "e.g., Conversions", "Keywords_or_Targeting_Layers": ["e.g., 'SaaS', 'productivity tools'"],
                    "Placement_Advice": "e.g., Target mobile feeds and Instagram stories."
                }}
            }},
            "image_orb": {{"title": "The Image Orb", "description": "Generate a stunning, scroll-stopping image for this campaign."}},
            "motion_orb": {{"title": "The Motion Orb", "description": "Generate a captivating, 15-second video ad for this campaign."}}
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def _prophesy_html_page(self, angle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates an SEO-optimized landing page with platform-specific guides."""
        platform = angle_data.get('platform', 'Netlify Drop')
        product_name = angle_data.get('product_name', '')
        logger.info(f"FORGING HTML PAGE: Platform='{platform}'")

        # DEEP-DIVE RAG
        tasks = {
            "deployment_guides": self.scout.find_niche_realms(f"how to deploy custom html on {platform}", num_results=3),
            "seo_guides": self.scout.find_niche_realms(f"seo best practices for {platform} site", num_results=3)
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        page_intel = {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}
        
        # FINAL, UPGRADED PROMPT
        prompt = f"""
        You are a master web developer and SEO guru. Your task is to generate a complete HTML page AND provide a custom deployment and SEO guide for a specific platform. Your goal is to turn every click into a customer and rank #1 on Google.

        --- PRIMARY INTEL ---
        - Product: {product_name}
        - Target Platform: {platform}
        - Strategic Angle: {json.dumps(angle_data.get('angle_id'), indent=2)}
        --- DEEP-DIVE INTELLIGENCE ---
        {json.dumps(page_intel, indent=2, default=str)}
        
        **Your Prophetic Task:**
        Generate a valid JSON object structured EXACTLY as follows:
        {{
            "html_code": {{ "title": "Complete Page HTML (SEO Optimized)", "content": "The full, single-file responsive HTML code. It MUST include SEO meta tags in the <head>, semantic HTML5 structure, and placeholder alt tags for images."}},
            "deployment_guide": {{
                "title": "Deployment & SEO Guide for {platform}",
                "content": {{
                    "Deployment": "A clear, step-by-step guide on how to publish the provided HTML code on {platform}, based on the research.",
                    "SEO_Configuration": "Actionable advice on configuring SEO settings specifically within the {platform} dashboard.",
                    "Ranking_Strategy": "Three advanced tips for improving the page's Google ranking over time."
                }}
            }},
            "image_prompts": [
                {{"section": "Header Image", "prompt": "A detailed AI art prompt for the main header image."}},
                {{"section": "Feature Section Image", "prompt": "A detailed AI art prompt for an image to illustrate a key benefit."}}
            ]
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def _prophesy_affiliate_review(self, angle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates multiple affiliate review options."""
        product_name = angle_data.get('product_name', '')
        logger.info(f"FORGING AFFILIATE REVIEWS for '{product_name}'")
        # This is a simpler case, no deep-dive RAG needed.
        prompt = f"""
        You are an expert affiliate marketer, known for writing authentic and high-converting product reviews.
        Your task is to generate three distinct review options for '{product_name}'.

        --- PRIMARY INTEL ---
        - Product: {product_name}
        - Strategic Angle: {json.dumps(angle_data.get('angle_id'), indent=2)}

        **Your Prophetic Task:**
        Generate a valid JSON object structured EXACTLY as follows:
        {{
            "reviews": [
                {{"title": "Review Option 1 (The Personal Story)", "content": "Write a review from the perspective of someone whose problem was solved by the product. Use a storytelling approach."}},
                {{"title": "Review Option 2 (The Feature Breakdown)", "content": "Write a detailed, analytical review focusing on the top 3 features and their benefits."}},
                {{"title": "Review Option 3 (The Quick Comparison)", "content": "Write a short, punchy review comparing this product to a common alternative and explaining why it's superior."}}
            ]
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)
# --- END OF FILE backend/stacks/marketing_saga_stack.py ---