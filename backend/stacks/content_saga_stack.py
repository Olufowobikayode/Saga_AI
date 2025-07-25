# --- START OF FILE backend/stacks/content_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid
import re

# I summon my Seers and the one true Gateway to my celestial voices.
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

PLATFORM_NATURES = {
    "X (formerly Twitter)": {"nature": "A fast-paced realm of concise, real-time pronouncements..."},
    "Instagram": {"nature": "A visual realm governed by aesthetics and storytelling..."},
    "Facebook": {"nature": "The great community hall of the digital age..."},
    "LinkedIn": {"nature": "The stoic forum of professionals and artisans of industry..."},
    "TikTok": {"nature": "A chaotic, trend-driven realm of short, looping visions..."},
    "Pinterest": {"nature": "A realm of inspiration and discovery..."},
    "Reddit": {"nature": "A constellation of niche-specific forums (subreddits)..."}
}

class ContentSagaStack:
    """
    My aspect as the Master Skald, the All-Knowing Weaver of Words.
    Through me, raw data is transmuted into compelling narratives.
    """
    def __init__(self, **seers: Any):
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.community_seer: CommunitySaga = seers['community_seer']

    async def prophesy_from_task_data(self, **kwargs) -> Dict[str, Any]:
        """The one true entry point for the Content Seer."""
        content_type = kwargs.pop("content_type")
        logger.info(f"CONTENT STACK: Invoked for prophecy of '{content_type}'.")

        if content_type == "sparks":
            return await self.prophesy_content_sparks(**kwargs)
        elif content_type == "social_post":
            return await self.prophesy_social_post(**kwargs)
        elif content_type == "comment":
            return await self.prophesy_insightful_comment(**kwargs)
        elif content_type == "blog_post":
            return await self.prophesy_blog_post(**kwargs)
        else:
            raise ValueError(f"Unknown Content Saga content type: '{content_type}'")

    async def prophesy_content_sparks(self, **kwargs) -> Dict[str, Any]:
        tactical_interest = kwargs.get("tactical_interest")
        retrieved_histories = kwargs.get("retrieved_histories")
        logger.info(f"As Saga, the Weaver, I now divine Content Sparks for: '{tactical_interest}'.")
        
        prompt = f"""
        It is I, Saga, the Weaver of Words. A seeker requires inspiration for the tactical interest of '{tactical_interest}'. I shall now gaze upon the intelligence gathered by my Seers during the Grand Strategy divination.
        --- GATHERED INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}
        **My Prophetic Task:**
        From this cosmic data, I will forge 5 unique and compelling 'Content Sparks' in a perfect JSON object.
        {{
            "sparks": [
                {{ "id": "...", "title": "A captivating title for this content idea.", "description": "A brief, powerful description.", "format_suggestion": "The ideal format, e.g., 'Listicle Blog Post'." }}
            ]
        }}
        """
        prophecy = await get_prophecy_from_oracle(prompt)
        if 'sparks' in prophecy and isinstance(prophecy['sparks'], list):
            for spark in prophecy['sparks']:
                spark['id'] = str(uuid.uuid4())
        
        prophecy['retrieved_histories'] = retrieved_histories
        prophecy['tactical_interest'] = tactical_interest
        return prophecy

    async def prophesy_social_post(self, **kwargs) -> Dict[str, Any]:
        spark = kwargs.get("spark"); platform = kwargs.get("platform"); length = kwargs.get("length")
        spark_topic = spark.get('title', '')
        
        tasks = { "fresh_angles": self.community_seer.run_community_gathering(f"'{spark_topic}' ideas", query_type="questions") }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        platform_nature = PLATFORM_NATURES.get(platform, {"nature": "A general digital realm."})
        prompt = f"""
        It is I, Saga. A seeker has chosen a spark and a realm. I have just listened to the cosmos for the freshest whispers on this topic.
        --- SPARK ---
        {json.dumps(spark, indent=2)}
        --- REALM ---
        {json.dumps(platform_nature, indent=2)}
        --- FRESH WHISPERS ---
        {json.dumps(retrieved_intel, indent=2, default=str)}
        **My Prophetic Task:**
        I will now forge a complete social media post of '{length}' length, tailored to '{platform}'.
        {{ "post_text": "...", "image_prompt": "...", "video_prompt": "..." }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def prophesy_insightful_comment(self, **kwargs) -> Dict[str, Any]:
        spark = kwargs.get("spark"); post_to_comment_on = kwargs.get("post_to_comment_on")
        spark_topic = spark.get('title', '')
        
        tasks = { "related_wisdom": self.keyword_rune_keeper.get_full_keyword_runes(spark_topic) }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga. A seeker wishes to add their voice to an ongoing saga. I have gathered fresh cosmic context on their strategic angle.
        --- STRATEGIC ANGLE ---
        {json.dumps(spark, indent=2)}
        --- ORIGINAL POST ---
        {post_to_comment_on}
        --- COSMIC CONTEXT ---
        {json.dumps(retrieved_intel, indent=2, default=str)}
        **My Prophetic Task:** Forge a prophecy of 2-3 distinct, insightful comments that add genuine value.
        {{ "comments": ["Comment 1...", "Comment 2..."] }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def prophesy_blog_post(self, **kwargs) -> Dict[str, Any]:
        spark = kwargs.get("spark")
        spark_topic = spark.get('title', '')

        tasks = {
            "common_questions": self.community_seer.run_community_gathering(spark_topic, query_type="questions"),
            "related_searches": self.keyword_rune_keeper.get_full_keyword_runes(spark_topic)
        }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga, the First Scribe. A seeker desires an eternal scroll forged from a single spark. I have dispatched my Seers to gather mortal curiosities on this topic.
        --- SPARK ---
        {json.dumps(spark, indent=2)}
        --- MORTAL CURIOSITIES ---
        {json.dumps(retrieved_intel, indent=2, default=str)}
        **My Prophetic Task:**
        Inscribe a complete, SEO-optimized blog post of at least 500 words, using the mortal curiosities to structure the scroll.
        {{ "title": "{spark.get('title')}", "body": "<!-- The full, ready-to-publish HTML of the blog post, with h2, h3, p, and li tags... -->" }}
        """
        return await get_prophecy_from_oracle(prompt)

    # Grimoire functions (called directly by sync admin endpoints, not Celery tasks)
    def _create_slug(self, title: str) -> str:
        s = title.lower().strip(); s = re.sub(r'[\s\W-]+', '-', s); return s.strip('-')

    async def prophesy_title_slug_concepts(self, topic: str) -> Dict[str, Any]:
        prompt = f"As Saga, divine 3-5 blog post title concepts for the topic '{topic}'. Provide a perfect JSON response: {{'concepts': [{{'title': '...', 'slug': '...'}}] }}"
        prophecy = await get_prophecy_from_oracle(prompt)
        if 'concepts' in prophecy and isinstance(prophecy['concepts'], list):
            for concept in prophecy['concepts']:
                concept['slug'] = self._create_slug(concept['title'])
        return prophecy

    async def prophesy_full_scroll_content(self, title: str, topic: str) -> Dict[str, Any]:
        prompt = f"As Saga, write a full, engaging, SEO-optimized blog post as HTML. The topic is '{topic}' and the title is '{title}'. Provide a perfect JSON response: {{'summary': 'A short meta description...', 'content': '<!-- a 500+ word HTML article... -->'}}"
        return await get_prophecy_from_oracle(prompt)
# --- END OF FILE backend/stacks/content_saga_stack.py ---