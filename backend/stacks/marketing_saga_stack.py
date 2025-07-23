# --- START OF FILE backend/stacks/marketing_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

import google.generativeai as genai

# --- Import Saga's Seers and Oracles ---
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
        """Initializes the stack with the AI oracle and all necessary seers for deep research."""
        self.model = model
        self.community_seer: CommunitySaga = seers['community_seer']
        # NEW: Add the other seers for enhanced research capabilities.
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.scout: MarketplaceScout = MarketplaceScout()


    async def prophesy_marketing_angles(self, product_name: str, product_description: str, target_audience: str, asset_type: str) -> Dict[str, Any]:
        """
        Phase 1: Performs enhanced research to propose several data-driven "angles".
        """
        logger.info(f"MARKETING SAGA (PHASE 1): Forging marketing angles for '{product_name}'...")
        
        # ENHANCED RAG: Now uses multiple seers for a richer intelligence picture.
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

        --- FRESH RESEARCH (What's working in 2025) ---
        {json.dumps(latest_trends, indent=2, default=str)}
        --- END RESEARCH ---

        **Your Prophetic Task:**
        Based on your deep research, generate 3-4 distinct, actionable "Marketing Angle Cards."

        Your output MUST be a valid JSON object with a single key, "marketing_angles", which is an array of objects, each with:
        - "angle_id": A unique identifier for this angle.
        - "title": A compelling name for this marketing strategy (e.g., "The 'Us vs. Them' Manifesto").
        - "description": A short explanation of the psychological principle behind this angle, based on your research.
        - "framework_steps": An array of steps outlining how to execute this angle.
        """
        angles_prophecy = await get_prophecy_from_oracle(self.model, prompt)
        
        if 'marketing_angles' in angles_prophecy and isinstance(angles_prophecy['marketing_angles'], list):
            for angle in angles_prophecy['marketing_angles']:
                angle['angle_id'] = str(uuid.uuid4())
        
        # Pass all necessary data to the next phase.
        angles_prophecy['product_name'] = product_name
        angles_prophecy['product_description'] = product_description
        angles_prophecy['target_audience'] = target_audience
        angles_prophecy['research_data'] = latest_trends

        return angles_prophecy

    async def prophesy_campaign_kit_from_angle(self, angle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates the complete 5-fold "Campaign Deployment Kit" for text-based assets.
        This now includes a second, deeper RAG phase.
        """
        asset_type = angle_data.get('asset_type', 'Ad Copy')
        product_name = angle_data.get('product_name', '')
        target_audience = angle_data.get('target_audience', '')
        logger.info(f"MARKETING SAGA (PHASE 2): Forging a full Campaign Kit for '{asset_type}'...")

        # NEW DEEP-DIVE RAG RITUAL
        tasks = {
            "targeting_guides": self.scout.find_niche_realms(f"how to target {target_audience} with Facebook ads", num_results=3),
            "platform_keywords": self.keyword_rune_keeper.get_full_keyword_runes(f"{product_name} ad keywords"),
            "conversion_questions": self.community_seer.run_community_gathering(f"what makes you buy {product_name} online", query_type="questions")
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        campaign_intel = {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}
        
        # UPGRADED MEGA-PROMPT
        generation_prompt = f"""
        You are a world-class performance marketer and media buyer. Your task is to generate a COMPLETE "Campaign Deployment Kit." Your goal is 100% conversion. Every part of your prophecy must be a sharp, actionable piece of intelligence.

        --- PRIMARY INTEL ---
        - Product: {product_name}
        - Target Audience: {target_audience}
        - Strategic Angle to Execute: {json.dumps(angle_data, indent=2)}
        
        --- NEW DEEP-DIVE CAMPAIGN INTELLIGENCE ---
        {json.dumps(campaign_intel, indent=2, default=str)}
        --- END INTELLIGENCE ---
        
        **Your Prophetic Task:**
        Generate the 5-fold prophecy. Your output MUST be a valid JSON object structured exactly as follows:
        {{
            "copy": {{"title": "The Scribe's Scroll ({asset_type})", "content": "The masterfully crafted, high-conversion copy, precisely following the strategic angle."}},
            "audience_rune": {{
                "title": "The Audience Rune (Targeting)", 
                "content": {{
                    "Demographics": "e.g., Age: 25-40, Gender: Both",
                    "Location": "e.g., USA, Canada, UK urban centers",
                    "Interests_and_Behaviors": ["e.g., Interested in sustainable technology, follows eco-friendly influencers, online shoppers"],
                    "Psychographics": "e.g., Values quality over price, seeks to minimize their environmental impact, feels guilty about waste."
                }}
            }},
            "platform_sigils": {{
                "title": "The Scribe's Sigils (Platform Setup)",
                "content": {{
                    "Platform_Suggestion": "e.g., Facebook & Instagram",
                    "Campaign_Objective": "e.g., Conversions",
                    "Keywords_or_Tags": ["e.g., sustainable gifts, eco kitchen, zero waste home"],
                    "Placement_Advice": "e.g., Target mobile feeds and Instagram stories. Avoid desktop right column."
                }}
            }},
            "image_orb": {{"title": "The Image Orb", "description": "Generate a stunning, scroll-stopping image for this campaign."}},
            "motion_orb": {{"title": "The Motion Orb", "description": "Generate a captivating, 15-second video ad for this campaign."}}
        }}
        """
        return await get_prophecy_from_oracle(self.model, generation_prompt)

    async def prophesy_page_html_from_angle(self, angle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a complete, SEO-optimized landing page with platform-specific deployment guides.
        """
        platform = angle_data.get('platform', 'Netlify Drop')
        product_name = angle_data.get('product_name', '')
        logger.info(f"MARKETING SAGA (PHASE 2): Forging an SEO-optimized page for '{platform}'...")

        # NEW DEEP-DIVE RAG RITUAL for HTML assets
        tasks = {
            "deployment_guides": self.scout.find_niche_realms(f"how to deploy custom html on {platform}", num_results=3),
            "seo_guides": self.scout.find_niche_realms(f"seo best practices for {platform} site", num_results=3)
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        page_intel = {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}
        
        # UPGRADED MEGA-PROMPT for HTML assets
        generation_prompt = f"""
        You are a master web developer and SEO guru. Your task is to generate a complete, single-file, responsive HTML page AND provide a custom deployment and SEO guide for a specific platform. Your goal is to turn every click into a customer and rank #1 on Google.

        --- PRIMARY INTEL ---
        - Product: {product_name}
        - Target Platform: {platform}
        - Strategic Angle to Execute: {json.dumps(angle_data, indent=2)}

        --- NEW DEEP-DIVE DEPLOYMENT INTELLIGENCE ---
        {json.dumps(page_intel, indent=2, default=str)}
        --- END INTELLIGENCE ---

        **Your Prophetic Task:**
        Generate a valid JSON object structured exactly as follows:
        {{
            "html_code": {{
                "title": "Complete Page HTML (SEO Optimized)",
                "content": "The full, single-file responsive HTML code. It MUST include SEO meta tags in the <head> (title, description), semantic HTML5 structure (header, main, section, footer), and placeholder alt tags for images."
            }},
            "deployment_guide": {{
                "title": "Deployment & SEO Guide for {platform}",
                "content": {{
                    "Step_1_Deployment": "A clear, step-by-step guide on how to publish the provided HTML code on {platform}, based on the research.",
                    "Step_2_SEO_Configuration": "Actionable advice on configuring SEO settings specifically within the {platform} dashboard.",
                    "Step_3_Ongoing_Ranking_Strategy": "Three advanced tips for improving the page's Google ranking over time."
                }}
            }},
            "image_prompts": [
                {{"section": "Header Image", "prompt": "A detailed prompt for an AI image generator for the main header image."}},
                {{"section": "Feature Section Image", "prompt": "A prompt for an image to illustrate a key benefit."}}
            ]
        }}
        """
        return await get_prophecy_from_oracle(self.model, generation_prompt)
# --- END OF FILE backend/stacks/marketing_saga_stack.py ---