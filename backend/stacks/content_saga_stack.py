--- START OF FILE backend/stacks/content_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid

import google.generativeai as genai

# --- Import Saga's Seers and Oracles ---
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

class ContentSagaStack:
    """
    A powerful, multi-phase stack for the Content Saga Prophecy.
    It guides a user from high-level ideas (sparks) to fully-formed, platform-specific content.
    """
    def __init__(self, model: genai.GenerativeModel, keyword_rune_keeper: KeywordRuneKeeper, community_seer: CommunitySaga):
        """Initializes the stack with the necessary tools for content divination."""
        self.model = model
        self.keyword_rune_keeper = keyword_rune_keeper
        self.community_seer = community_seer

    async def _gather_base_histories(self, interest: str) -> Dict[str, Any]:
        """Gathers the foundational keyword and community data for a content saga."""
        tasks = {
            "keyword_runes": self.keyword_rune_keeper.get_full_keyword_runes(interest, None),
            "community_questions": self.community_seer.run_community_gathering(interest, None, None),
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return {key: res for key, res in zip(tasks.keys(), results) if not isinstance(res, Exception)}

    async def prophesy_content_sparks(self, interest: str, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        """
        Phase 1: Generates 5 high-level, actionable content ideas ("sparks").
        """
        logger.info(f"CONTENT SAGA (PHASE 1): Divining 5 content sparks for interest: '{interest}'")
        retrieved_histories = await self._gather_base_histories(interest)
        
        prompt = f"""
        You are Saga's Skald, a master storyteller. A creator, interested in '{interest}', seeks your inspiration. They may also have a link they wish to promote:
        - Link: {link or 'Not provided.'}
        - Link Description: {link_description or 'Not provided.'}

        Your first task is to reveal 5 "Content Sparks"—core ideas for content, grounded in the real questions and search terms of their audience.

        --- AUDIENCE WHISPERS (Retrieved Histories) ---
        {json.dumps(retrieved_histories, indent=2)}
        --- END OF HISTORIES ---

        Your Prophetic Task: From the histories, forge 5 unique Content Sparks. For each, provide:
        1. "spark_id": A unique identifier for this idea.
        2. "title": A compelling, clickable title for a piece of content.
        3. "description": A short hook explaining what problem it solves or what question it answers, based on the data.

        Your output MUST be a valid JSON object with a single key "sparks" which is an array of these 5 objects.
        """
        prophecy = await get_prophecy_from_oracle(self.model, prompt)
        return {
            "sparks": prophecy.get("sparks", []),
            "retrieved_histories": retrieved_histories # Cache this for phase 2
        }

    async def prophesy_social_post(self, spark: Dict, platform: str, length: str, post_type: str, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        """Generates a specific social media post for a chosen spark and platform."""
        logger.info(f"CONTENT SAGA (POST): Weaving a '{length}' '{post_type}' post for '{platform}' based on spark: '{spark.get('title')}'")

        prompt = f"""
        You are a master social media strategist, adapting a core content idea for a specific platform.
        
        Core Idea (Content Spark): {json.dumps(spark, indent=2)}
        Target Platform: {platform}
        Desired Length: {length}
        Desired Type/Tone: {post_type}
        Promotional Link: {link or 'None'}
        Link Description: {link_description or 'None'}

        **Your Task:** Write a social media post that perfectly fits the requirements.
        - **Platform Nature:** Consider the platform. For 'X', use hashtags and a direct tone. For 'Instagram', be visual. For 'LinkedIn', be professional. For 'TikTok', write a script idea. For 'Facebook', be community-focused.
        - **Length:** Adhere strictly to the requested length ('Short' = 1-2 sentences, 'Medium' = a paragraph, 'Long/Thread' = multiple numbered paragraphs).
        - **Type:** Embody the requested tone ('Fun', 'Educational', 'Engaging').
        - **Link Integration:** If a link is provided, weave it in naturally. Do not just paste it at the end. For a product, you might say "Check out the [link_description] we use...". For a community, "Join fellow enthusiasts at...".

        Your output MUST be a valid JSON object with the following keys:
        {{
            "post_text": "The fully generated social media post text, ready to be copied.",
            "image_prompt": "A descriptive prompt for an AI image generator (like Midjourney or DALL-E) to create a compelling visual for this post. Be detailed.",
            "video_prompt": "A prompt for an AI video generator (like Sora or Runway). Describe a short video clip, including scene, action, and style, that would accompany this post."
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_insightful_comment(self, spark: Dict, post_to_comment_on: str, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        """Generates an insightful comment to engage a community and drive traffic."""
        logger.info(f"CONTENT SAGA (COMMENT): Weaving an insightful comment related to spark: '{spark.get('title')}'")

        prompt = f"""
        You are a community engagement expert. Your goal is to write a non-spammy, genuinely insightful comment on a social media post to build authority and subtly guide people to your profile.

        The Post I am commenting on: "{post_to_comment_on}"

        My Own Related Content Idea (My Angle): {json.dumps(spark, indent=2)}
        My Promotional Link (Optional): {link or 'None'}
        My Link's Description: {link_description or 'None'}

        **Your Task:** Write an insightful comment.
        1.  **Add Value First:** Directly address the original post. Agree, disagree respectfully, or add a new perspective.
        2.  **Bridge to Your Angle:** Smoothly transition to your own area of expertise (the "spark"). For example, "This is a great point! It reminds me of the challenges with [topic from your spark]..."
        3.  **Subtle Promotion (If Link Provided):** DO NOT just paste the link. Instead, allude to it. Example: "I actually wrote a detailed guide on solving the [spark problem] for my community newsletter." The goal is to make people click on your profile, not to spam a link in the comments.

        Your output MUST be a valid JSON object with a single key:
        {{
            "comment_text": "The fully generated, insightful comment text, ready to be copied."
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_blog_post(self, spark: Dict, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        """Generates a full-length blog post from a content spark."""
        logger.info(f"CONTENT SAGA (BLOG): Weaving a full blog post for spark: '{spark.get('title')}'")
        
        prompt = f"""
        You are an expert long-form content writer and SEO specialist. Your task is to expand a "Content Spark" into a complete, well-structured blog post.

        Core Idea (Content Spark): {json.dumps(spark, indent=2)}
        Promotional Link to Include: {link or 'None'}
        Link Description: {link_description or 'None'}

        **Your Task:** Write a complete blog post of at least 500 words.
        - **Structure:** Use clear headings, subheadings, lists, and bold text to make it easy to read.
        - **Content:** Elaborate deeply on the spark's title and description. Answer the core question thoroughly.
        - **Placeholders:** You MUST include the following placeholders within the text where they would naturally fit:
            - `[INSERT COMPELLING IMAGE HERE]`
            - `[INSERT YOUR AFFILIATE LINK FOR A RELATED PRODUCT HERE]`
            - (If a link was provided by the user) `[INSERT USER'S LINK: {link_description}]`

        Your output MUST be a valid JSON object with the following keys:
        {{
            "blog_post_title": "{spark.get('title')}",
            "blog_post_body": "The full, ready-to-publish HTML-formatted text of the blog post.",
            "image_prompts": [
                {{"section": "Header Image", "prompt": "A detailed prompt for an AI image generator for the main blog header image."}},
                {{"section": "Mid-post Illustration", "prompt": "A prompt for an image to illustrate a key point in the middle of the article."}}
            ]
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

--- END OF FILE backend/stacks/content_saga_stack.py ---