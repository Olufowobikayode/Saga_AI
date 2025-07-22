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

# --- SAGA'S PLATFORM GRIMOIRE ---
# This dictionary is a masterpiece of prompt engineering and requires no changes.
PLATFORM_NATURES = {
    # Mainstream Giants
    "Facebook": {"content_type": "Hybrid", "primary_audience": "General / Community", "tone_and_style": "Community-focused, conversational, supports text, images, and video. Good for groups and local engagement."},
    "YouTube": {"content_type": "Video", "primary_audience": "General / Entertainment / Education", "tone_and_style": "Long-form video, educational content, vlogs, tutorials. Requires high-quality video production."},
    "Instagram": {"content_type": "Image", "primary_audience": "General / Lifestyle / Visual", "tone_and_style": "Visually-driven, high-quality images and short videos (Reels). Captions are secondary but should be engaging and use relevant hashtags."},
    "TikTok": {"content_type": "Video", "primary_audience": "Gen Z / Entertainment", "tone_and_style": "Short-form, trend-driven, authentic video. Music and effects are key. High energy and creativity are rewarded."},
    "X (formerly Twitter)": {"content_type": "Text", "primary_audience": "General / News / Tech", "tone_and_style": "Short, concise text updates (posts/threads), real-time conversation, news-jacking, use of hashtags is critical."},
    "LinkedIn": {"content_type": "Text", "primary_audience": "Professional Network", "tone_and_style": "Professional, insightful articles and posts. Focus on career, business, and industry insights. Formal tone."},
    "Pinterest": {"content_type": "Image", "primary_audience": "Visual Discovery / DIY / Lifestyle", "tone_and_style": "High-quality vertical images (Pins) that link to external sites. Focus on inspiration, tutorials, and product discovery."},
    "Reddit": {"content_type": "Text", "primary_audience": "Niche Communities", "tone_and_style": "Community-specific, authentic, text-heavy posts. Overt self-promotion is heavily discouraged. Add value to subreddits."},
    # ... The rest of the comprehensive PLATFORM_NATURES dictionary remains unchanged ...
}

class ContentSagaStack:
    """
    A powerful, multi-phase stack for the Content Saga Prophecy.
    It guides a user from high-level ideas (sparks) to fully-formed, platform-specific content,
    acting upon intelligence gathered by the GrandStrategyStack.
    """
    def __init__(self, model: genai.GenerativeModel, keyword_rune_keeper: KeywordRuneKeeper, community_seer: CommunitySaga):
        """Initializes the stack with the connection to the AI oracle."""
        self.model = model
        # The seers are kept for potential future standalone use, but the primary workflow will receive data.
        self.keyword_rune_keeper = keyword_rune_keeper
        self.community_seer = community_seer

    async def prophesy_content_sparks(self, tactical_interest: str, retrieved_histories: Dict[str, Any], link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        """
        Phase 1: Generates 5 high-level, actionable content ideas ("sparks").
        This method now receives its intelligence directly, ensuring strategic cohesion.
        """
        logger.info(f"CONTENT SAGA (PHASE 1): Divining 5 content sparks for interest: '{tactical_interest}'")
        
        # This stack no longer gathers its own data, it receives it from the engine's cache.
        # This is a critical architectural improvement for efficiency and consistency.

        prompt = f"""
        You are Saga's Skald, a master storyteller and content strategist. A creator, interested in '{tactical_interest}', seeks your inspiration. You must forge your prophecy from the grand intelligence already gathered.

        --- STRATEGIC INTELLIGENCE (Retrieved Histories) ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        --- END OF INTELLIGENCE ---

        The creator may also wish to promote a specific link:
        - Link: {link or 'Not provided.'}
        - Link Description: {link_description or 'Not provided.'}

        Your Prophetic Task: From the rich tapestry of the provided intelligence, forge 5 unique "Content Sparks." These are the seeds of great sagas.
        For each spark, you MUST provide:
        1. "spark_id": A unique identifier for this idea.
        2. "title": A compelling, clickable title for a piece of content (e.g., a blog post, video, or thread).
        3. "description": A short, powerful hook explaining what problem it solves or what question it answers, directly referencing the gathered intelligence.
        4. "format_suggestion": The best format for this idea (e.g., "Listicle Blog Post," "Short-form Video Tutorial," "Expert Interview," "Data-driven Infographic").

        Your output MUST be a valid JSON object with a single key "sparks" which is an array of these 5 spark objects.
        """
        prophecy = await get_prophecy_from_oracle(self.model, prompt)
        
        # Manually add unique IDs to each spark after generation for robust tracking.
        if 'sparks' in prophecy and isinstance(prophecy['sparks'], list):
            for spark in prophecy['sparks']:
                spark['spark_id'] = str(uuid.uuid4())

        return prophecy # The histories are no longer returned as they were passed in.

    async def prophesy_social_post(self, spark: Dict, platform: str, length: str, post_type: str, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        """Generates a specific social media post by consulting the Platform Grimoire."""
        logger.info(f"CONTENT SAGA (POST): Weaving a '{length}' '{post_type}' post for '{platform}' from spark: '{spark.get('title')}'")

        platform_details = PLATFORM_NATURES.get(platform, {
            "content_type": "Hybrid", 
            "primary_audience": "General", 
            "tone_and_style": "Generic, flexible tone."
        })

        prompt = f"""
        You are a master social media strategist, adapting a core content idea for a specific platform by consulting Saga's Grimoire.
        
        **Core Idea (Content Spark):** {json.dumps(spark, indent=2)}
        
        **Target Platform:** {platform}
        
        **Platform's Nature (from the Grimoire):** 
        - Primary Content Type: {platform_details['content_type']}
        - Tone & Style Guidance: {platform_details['tone_and_style']}
        
        **Your Directives:**
        - Desired Length: {length}
        - Desired Type/Tone: {post_type}
        - Promotional Link: {link or 'None'}
        - Link Description: {link_description or 'None'}

        **Your Task:** Write a social media post that perfectly fits all directives and the platform's nature.
        - **Adhere to the Grimoire:** The 'Tone & Style Guidance' is your primary law. If it says "professional," be professional. If it says "trend-driven video," your output should be a script for such a video.
        - **Length:** Strictly follow the requested length ('Short', 'Medium', 'Long/Thread').
        - **Type:** Embody the requested tone ('Fun', 'Educational', 'Engaging').
        - **Link Integration:** Weave the link in naturally, as previously instructed.

        Your output MUST be a valid JSON object with the following keys:
        {{
            "post_text": "The fully generated social media post text, ready to be copied. For video platforms, this should be a script or a detailed scene description.",
            "image_prompt": "A descriptive prompt for an AI image generator (like Midjourney or DALL-E) to create a compelling visual for this post. Be detailed.",
            "video_prompt": "A prompt for an AI video generator (like Sora or Runway). Describe a short video clip, including scene, action, and style, that would accompany this post."
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_insightful_comment(self, spark: Dict, post_to_comment_on: str, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        """Generates an insightful comment to engage a community and drive traffic."""
        logger.info(f"CONTENT SAGA (COMMENT): Weaving an insightful comment from spark: '{spark.get('title')}'")

        prompt = f"""
        You are a community engagement expert. Your goal is to write a non-spammy, genuinely insightful comment on a social media post to build authority and subtly guide people to your profile.

        The Post I am commenting on: "{post_to_comment_on}"

        My Own Related Content Idea (My Angle): {json.dumps(spark, indent=2)}
        My Promotional Link (Optional): {link or 'None'}
        My Link's Description: {link_description or 'None'}

        **Your Task:** Write an insightful comment.
        1.  **Add Value First:** Directly address the original post. Agree, disagree respectfully, or add a new perspective. Your comment must feel like a genuine contribution to the conversation.
        2.  **Bridge to Your Angle:** Smoothly transition to your own area of expertise (the "spark").
        3.  **Subtle Promotion (If Link Provided):** DO NOT just paste the link. Instead, allude to it. Example: "I actually wrote a detailed guide on this exact topic, you can find it on my profile if you're interested."

        Your output MUST be a valid JSON object with a single key:
        {{
            "comment_text": "The fully generated, insightful comment text, ready to be copied."
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

    async def prophesy_blog_post(self, spark: Dict, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        """Generates a full-length blog post from a content spark."""
        logger.info(f"CONTENT SAGA (BLOG): Weaving a full blog post from spark: '{spark.get('title')}'")
        
        prompt = f"""
        You are an expert long-form content writer and SEO specialist. Your task is to expand a "Content Spark" into a complete, well-structured blog post.

        Core Idea (Content Spark): {json.dumps(spark, indent=2)}
        Promotional Link to Include: {link or 'None'}
        Link Description: {link_description or 'None'}

        **Your Task:** Write a complete blog post of at least 500 words.
        - **Structure:** Use clear headings (H2, H3), subheadings, lists, and bold text for readability.
        - **Content:** Elaborate deeply on the spark's title and description. Answer the underlying question thoroughly.
        - **Placeholders:** You MUST include the following placeholders where they would naturally fit: `[INSERT COMPELLING IMAGE HERE]`, `[INSERT YOUR AFFILIATE LINK FOR A RELATED PRODUCT HERE]`, and (If user link provided) `[INSERT USER'S LINK: {link_description}]`.

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