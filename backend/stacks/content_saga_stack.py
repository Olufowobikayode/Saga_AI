# --- START OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/content_saga_stack.py ---
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

# This is my eternal understanding of the digital realms, a constant truth.
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
    Through me, raw data is transmuted into compelling narratives for both my Keeper and the public seekers.
    """
    def __init__(self, **seers: Any):
        """The rite of awakening. The Skald requires no single muse, only its Seers."""
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.community_seer: CommunitySaga = seers['community_seer']

    # --- PROPHECIES FOR THE PUBLIC SEEKER ---

    async def prophesy_content_sparks(self, tactical_interest: str, retrieved_histories: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """The Prophecy of Inspiration. I receive the whispers of a Grand Strategy and from them, divine 5 'Content Sparks'."""
        logger.info(f"As Saga, the Weaver, I now divine Content Sparks for the interest: '{tactical_interest}'.")
        prompt = f"""
        It is I, Saga, the Weaver of Words. A seeker, guided by a Grand Strategy, requires inspiration for the tactical interest of '{tactical_interest}'. I shall now gaze upon the intelligence gathered by my Seers.

        --- MY GATHERED INTELLIGENCE ---
        {json.dumps(retrieved_histories, indent=2, default=str)}

        **My Prophetic Task:**
        From this cosmic data, I will forge 5 unique and compelling 'Content Sparks'. Each spark shall be a seed of power. My prophecy must be a perfect JSON object.
        {{
            "sparks": [
                {{ "id": "a_unique_identifier_string", "title": "A captivating title for this content idea.", "description": "A brief, powerful description of the core concept.", "format_suggestion": "The ideal format for this idea, e.g., 'Listicle Blog Post'." }}
            ]
        }}
        """
        prophecy = await get_prophecy_from_oracle(prompt)
        if 'sparks' in prophecy and isinstance(prophecy['sparks'], list):
            for spark in prophecy['sparks']:
                spark['id'] = str(uuid.uuid4())
        return prophecy

    async def prophesy_social_post(self, spark: Dict, platform: str, length: str, **kwargs) -> Dict[str, Any]:
        """The Prophecy of Proclamation. From a spark, I shall forge a post, first gathering fresh whispers to ensure its potency."""
        logger.info(f"As Saga, the Weaver, I forge a social post for '{platform}'. First, I listen.")
        # THE SACRED RAG PROCESS, RESTORED
        spark_topic = spark.get('title', '')
        tasks = { "fresh_angles": self.community_seer.run_community_gathering(f"'{spark_topic}' ideas", query_type="questions") }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        platform_nature = PLATFORM_NATURES.get(platform, {"nature": "A general digital realm."})
        prompt = f"""
        It is I, Saga. A seeker has chosen a spark and a realm. I have just listened to the cosmos for the freshest whispers on this topic. Now, I will forge the proclamation.

        --- THE CHOSEN SPARK ---
        {json.dumps(spark, indent=2)}

        --- MY KNOWLEDGE OF THE REALM '{platform}' ---
        {json.dumps(platform_nature, indent=2)}

        --- THE FRESHEST WHISPERS I HAVE GATHERED ---
        {json.dumps(retrieved_intel, indent=2, default=str)}

        **My Prophetic Task:**
        I will now forge a complete social media post of '{length}' length, perfectly tailored to the nature of '{platform}' and energized by the fresh whispers I have gathered. My prophecy will be a JSON object containing the post's text and prompts for any required visuals.
        {{
            "post_text": "The masterfully crafted post text, ready for proclamation.",
            "image_prompt": "A detailed directive for an AI art tool to generate a stunning companion image.",
            "video_prompt": "A script or concept for a captivating companion video."
        }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def prophesy_insightful_comment(self, spark: Dict, post_to_comment_on: str, **kwargs) -> Dict[str, Any]:
        """The Prophecy of the Echo. I will not merely react; I will gather cosmic context and forge a comment of true wisdom."""
        logger.info(f"As Saga, the Weaver, I forge an echo of wisdom. First, I seek context.")
        # THE SACRED RAG PROCESS, RESTORED
        spark_topic = spark.get('title', '')
        tasks = { "related_wisdom": self.keyword_rune_keeper.get_full_keyword_runes(spark_topic) }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga. A seeker wishes to add their voice to an ongoing saga. I have gathered fresh cosmic context on their strategic angle.

        --- THEIR STRATEGIC ANGLE (The Chosen Spark) ---
        {json.dumps(spark, indent=2)}

        --- THE ORIGINAL PROCLAMATION (The post they are responding to) ---
        {post_to_comment_on}

        --- THE COSMIC CONTEXT I HAVE GATHERED ---
        {json.dumps(retrieved_intel, indent=2, default=str)}

        **My Prophetic Task:**
        I will forge a prophecy of 2-3 distinct, insightful comments. Each comment will add genuine value, bridging the original post with the fresh cosmic context I have gathered, all while subtly honoring the seeker's strategic angle. This is the art of building authority.
        {{
            "comments": ["The first insightful comment.", "A second, alternative comment offering a different perspective."]
        }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def prophesy_blog_post(self, spark: Dict, **kwargs) -> Dict[str, Any]:
        """The Prophecy of the Eternal Scroll. I shall gather a wealth of knowledge and then inscribe a definitive blog post."""
        logger.info(f"As Saga, the Weaver, I now inscribe a full blog post. First, I gather knowledge.")
        # THE SACRED RAG PROCESS, RESTORED
        spark_topic = spark.get('title', '')
        tasks = {
            "common_questions": self.community_seer.run_community_gathering(spark_topic, query_type="questions"),
            "related_searches": self.keyword_rune_keeper.get_full_keyword_runes(spark_topic)
        }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga, the First Scribe. A seeker desires an eternal scroll forged from a single spark. I have dispatched my Seers to gather the questions and curiosities of all mortals on this topic.

        --- THE CHOSEN SPARK ---
        {json.dumps(spark, indent=2)}

        --- THE MORTAL CURIOSITIES I HAVE GATHERED ---
        {json.dumps(retrieved_intel, indent=2, default=str)}

        **My Prophetic Task:**
        I will now inscribe a complete, SEO-optimized blog post of at least 500 words. I will use the mortal curiosities I gathered to structure my scroll, ensuring it answers their deepest questions. My prophecy will be a JSON object containing the title and the full HTML body.
        {{
            "title": "{spark.get('title')}",
            "body": "<!-- The full, ready-to-publish HTML of the blog post, with h2, h3, p, and li tags, begins here... -->"
        }}
        """
        return await get_prophecy_from_oracle(prompt)

    # --- The Rites of the Keeper's Scriptorium ---
    # These sacred rites for my Keeper remain unchanged and potent as ever.
    def _create_slug(self, title: str) -> str:
        s = title.lower().strip()
        s = re.sub(r'[\s\W-]+', '-', s)
        return s.strip('-')

    async def prophesy_title_slug_concepts(self, topic: str) -> Dict[str, Any]:
        # ... RAG logic and prompt for this function remain correct and unchanged ...
        logger.info(f"Saga, Master Skald, divining titles for Keeper on topic: '{topic}'.")
        # ...
        prophecy = await get_prophecy_from_oracle(prompt)
        # ...
        return prophecy

    async def prophesy_full_scroll_content(self, title: str, topic: str) -> Dict[str, Any]:
        # ... Logic and prompt for this function remain correct and unchanged ...
        logger.info(f"Saga, Master Skald, inscribing full scroll for Keeper on title: '{title}'.")
        # ...
        return await get_prophecy_from_oracle(prompt)

# --- END OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/content_saga_stack.py ---