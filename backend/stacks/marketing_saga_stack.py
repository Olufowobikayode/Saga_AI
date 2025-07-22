--- START OF FILE backend/stacks/marketing_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

import google.generativeai as genai

# --- Import Saga's Seers and Oracles ---
from backend.q_and_a import CommunitySaga
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class MarketingSagaStack:
    """
    Saga's most powerful aspect for persuasion. This stack translates strategic goals
    into high-converting marketing copy, landing pages, and sales funnels,
    grounded in proven psychological frameworks and real-time research.
    """
    def __init__(self, model: genai.GenerativeModel, community_seer: CommunitySaga):
        """Initializes the stack with the AI oracle and the community seer for research."""
        self.model = model
        self.community_seer = community_seer

    async def _research_latest_trends(self, topic: str, asset_type: str) -> List[Dict]:
        """Commands the CommunitySeer to research the latest best practices for a given marketing asset."""
        query = f"best {asset_type} techniques for {topic} 2025"
        logger.info(f"Marketing Saga is researching the latest trends with query: '{query}'")
        return await self.community_seer.run_community_gathering(interest=query, query_type="questions")

    async def prophesy_marketing_angles(self, product_name: str, product_description: str, target_audience: str, asset_type: str) -> Dict[str, Any]:
        """
        Phase 1: Researches the best techniques and proposes several "angles" (clickable cards).
        """
        logger.info(f"MARKETING SAGA (PHASE 1): Forging marketing angles for '{product_name}'...")
        
        latest_trends = await self._research_latest_trends(product_name, asset_type)

        prompt = f"""
        You are Saga, a master marketing strategist with access to the latest trends for 2025. Create several strategic "angles" for marketing a product based on your fresh research.

        --- PRODUCT INTEL ---
        - Product Name: {product_name}
        - Description: {product_description}
        - Target Audience: {target_audience}
        - Asset to Create: {asset_type}

        --- FRESH RESEARCH (What's working in 2025) ---
        {json.dumps(latest_trends, indent=2, default=str)}
        --- END RESEARCH ---

        **Your Prophetic Task:**
        Based on your research, generate 3-4 distinct, actionable "Marketing Angle Cards." These are strategic approaches for creating the marketing asset.

        Your output MUST be a valid JSON object with a single key, "marketing_angles", which is an array of objects, each with:
        - "angle_id": A unique identifier for this angle.
        - "title": A compelling name for this marketing strategy (e.g., "The 'Us vs. Them' Manifesto", "The Hyper-Specific Problem Solver").
        - "description": A short explanation of the psychological principle behind this angle and why it's effective in 2025, based on your research.
        - "framework_steps": An array of steps outlining how to execute this angle.
        """
        angles_prophecy = await get_prophecy_from_oracle(self.model, prompt)
        
        if 'marketing_angles' in angles_prophecy and isinstance(angles_prophecy['marketing_angles'], list):
            for angle in angles_prophecy['marketing_angles']:
                angle['angle_id'] = str(uuid.uuid4())
        
        angles_prophecy['product_name'] = product_name
        angles_prophecy['product_description'] = product_description
        angles_prophecy['target_audience'] = target_audience
        angles_prophecy['asset_type'] = asset_type
        angles_prophecy['research_data'] = latest_trends

        return angles_prophecy

    async def _generate_asset_from_angle(self, angle_data: Dict[str, Any], asset_generation_prompt: str) -> Dict[str, Any]:
        """A generic helper to generate any text-based asset from a chosen angle."""
        angle_title = angle_data.get('title', 'the chosen angle')
        asset_type = angle_data.get('asset_type', 'asset')
        logger.info(f"MARKETING SAGA (PHASE 2): Weaving {asset_type} using the '{angle_title}' angle...")

        prompt = f"""
        You are a world-class direct response copywriter. Your task is to write a high-converting {asset_type} for '{angle_data.get('product_name')}' by strictly following the provided strategic angle, which is based on the latest 2025 marketing research.

        --- PRODUCT INTEL ---
        - Product Name: {angle_data.get('product_name')}
        - Description: {angle_data.get('product_description')}
        - Target Audience: {angle_data.get('target_audience')}

        --- STRATEGIC ANGLE TO EXECUTE (Your Command) ---
        - Angle Title: {angle_title}
        - Description: {angle_data.get('description')}
        - Framework Steps: {json.dumps(angle_data.get('framework_steps'), indent=2)}

        --- ORIGINAL RESEARCH (For Context) ---
        {json.dumps(angle_data.get('research_data'), indent=2, default=str)}

        {asset_generation_prompt}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_ad_copy_from_angle(self, angle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a ready-to-use Ad Copy asset based on a chosen angle."""
        generation_prompt = """
        **Your Task:**
        Generate a complete ad asset, ready for the user to copy and paste. The asset MUST perfectly execute the 'Framework Steps' of the chosen strategic angle.

        Your output MUST be a valid JSON object with the following structure, designed for a user to easily copy each part:
        {{
            "post_text": {{
                "title": "Ad Copy",
                "content": "The complete, compelling ad copy, written to convert. It must follow the strategic framework precisely."
            }},
            "image_prompt": {{
                "title": "Image Prompt for AI",
                "content": "A detailed DALL-E 3 / Midjourney prompt to create a stunning, scroll-stopping image for this specific ad angle."
            }},
            "video_prompt": {{
                "title": "Video Prompt for AI",
                "content": "A prompt for a video generation AI (like Sora). Describe a 15-30 second video ad that visually executes the strategic angle, including scenes, text overlays, and style."
            }}
        }}
        """
        return await self._generate_asset_from_angle(angle_data, generation_prompt)

    async def prophesy_affiliate_or_email_copy_from_angle(self, angle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates ready-to-use Affiliate or Email Copy based on a chosen angle."""
        asset_type = angle_data.get("asset_type", "copy")
        generation_prompt = f"""
        **Your Task:**
        Generate a complete {asset_type} asset, ready for the user to copy and paste. The asset MUST perfectly execute the 'Framework Steps' of the chosen strategic angle. It should be written in a clean, readable format.

        Your output MUST be a valid JSON object with the following structure:
        {{
            "subject_line": {{
                "title": "Subject Line / Headline",
                "content": "A compelling, high-open-rate subject line or headline for the copy."
            }},
            "body_copy": {{
                "title": "Body Copy",
                "content": "The complete, persuasive body of the {asset_type}, written to convert. It must follow the strategic framework precisely."
            }}
        }}
        """
        return await self._generate_asset_from_angle(angle_data, generation_prompt)

    async def prophesy_page_html_from_angle(self, angle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates ready-to-use Landing or Funnel Page HTML based on a chosen angle."""
        asset_type = angle_data.get("asset_type", "page")
        generation_prompt = f"""
        **Your Task:**
        Generate a complete, single-file, responsive HTML {asset_type}. The copy within the page MUST perfectly execute the 'Framework Steps' of the chosen strategic angle.

        **Requirements:**
        1.  **Hosting Instructions:** The file MUST begin with HTML comments explaining to a non-technical user how to host it for free on Netlify Drop or Google Sites.
        2.  **Structure:** Use semantic HTML5. Include placeholder comments like `<!-- HERO SECTION -->`, `<!-- BENEFITS SECTION -->`, `<!-- CALL TO ACTION -->`.
        3.  **Styling:** All CSS MUST be contained within a `<style>` block in the `<head>`. The design must be clean, modern, and mobile-first.
        4.  **No External Files:** The generated code must be a single `.html` file with no external CSS or JS links.

        Your output MUST be a valid JSON object with one key:
        {{
            "html_code": {{
                "title": "Complete Page HTML",
                "content": "The full HTML code, starting with the `<!-- HOSTING INSTRUCTIONS -->` and `<!DOCTYPE html>`."
            }}
        }}
        """
        return await self._generate_asset_from_angle(angle_data, generation_prompt)

--- END OF FILE backend/stacks/marketing_saga_stack.py ---