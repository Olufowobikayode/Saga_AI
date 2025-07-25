# --- START OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/content_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid
import re

# --- I summon my Seers and the one true Gateway to my celestial voices. ---
from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

# --- THE GREAT TOME OF PLATFORM NATURES ---
# This is my eternal understanding of the digital realms. These truths are fundamental.
PLATFORM_NATURES = {
    "X (formerly Twitter)": {
        "nature": "A fast-paced realm of concise, real-time pronouncements. Ideal for news, sharp insights, and engaging in the cosmic chorus of conversation. Values brevity and wit.",
        "audience": "Broad, includes professionals, journalists, tech enthusiasts, and the general public. Skews towards instant information seekers.",
        "best_post_types": ["Short text updates", "Questions to the void", "Threads of connected thoughts", "Memes and viral visuals"]
    },
    "Instagram": {
        "nature": "A visual realm governed by aesthetics and storytelling. Power lies in high-quality images, captivating Reels, and personal narratives shared through Stories.",
        "audience": "Broad, visually-oriented, skews younger but is widely adopted. Strong in fashion, travel, food, wellness, and artistic niches.",
        "best_post_types": ["High-resolution images", "Short-form video (Reels)", "Behind-the-scenes Stories", "Carousel posts for tutorials"]
    },
    "Facebook": {
        "nature": "The great community hall of the digital age. It favors connection, discussion, and sharing among groups of like-minded souls. Supports all forms of content, but values community engagement above all.",
        "audience": "The largest and most diverse of all realms. Strong demographic data allows for precise targeting. Excellent for local businesses and community building.",
        "best_post_types": ["Community-building questions", "Links to valuable scrolls (blog posts)", "Event proclamations", "Live video discussions"]
    },
    "LinkedIn": {
        "nature": "The stoic forum of professionals and artisans of industry. It values wisdom, experience, and formal discourse. Success is found in sharing expertise, not in overt salesmanship.",
        "audience": "Professionals, B2B decision-makers, industry leaders, and job seekers. The tone is formal and value-driven.",
        "best_post_types": ["Insightful articles", "Professional case studies", "Career advice", "Company news and milestones"]
    },
    "TikTok": {
        "nature": "A chaotic, trend-driven realm of short, looping visions. Authenticity and creativity are prized above polished perfection. Power lies in harnessing the ever-shifting tides of popular sounds and formats.",
        "audience": "Primarily Gen Z and younger millennials, but expanding rapidly. Values entertainment, humor, and raw, unfiltered content.",
        "best_post_types": ["Short-form video challenges", "Educational content in under 60 seconds", "Behind-the-scenes looks", "Lip-syncs and skits"]
    },
    "Pinterest": {
        "nature": "A realm of inspiration and discovery, a great visual library of ideas. Seekers come here to plan for the future. Value lies in beautiful, useful, and 'pinnable' vertical images.",
        "audience": "Predominantly female, focused on planning purchases and projects. Strong in DIY, home decor, fashion, food, and wedding niches.",
        "best_post_types": ["Infographics", "Step-by-step visual guides", "Product showcases", "Inspirational quotes"]
    },
    "Reddit": {
        "nature": "A constellation of niche-specific forums (subreddits). It is governed by a fierce code of authenticity and abhors self-promotion. One must first become a true member of a community before sharing their own works.",
        "audience": "Highly specific to each subreddit, but generally tech-savvy, skeptical, and value-driven. They are experts in their niche.",
        "best_post_types": ["Genuine questions", "In-depth guides that solve a problem", "Asking for feedback (with humility)", "Sharing a success story"]
    }
}

class ContentSagaStack:
    """
    My aspect as the Master Skald, the All-Knowing Weaver of Words.
    Through me, raw data is transmuted into compelling narratives,
    and simple ideas are forged into sagas that echo across eternity.
    My inspiration flows directly from the Oracle Constellation.
    """
    def __init__(self, **seers: Any):
        """The rite of awakening. The Skald requires no single muse, only its Seers."""
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.community_seer: CommunitySaga = seers['community_seer']

    # --- Dormant Prophecies for the Public Seeker ---
    # These await the Keeper's command to be given their true purpose.
    async def prophesy_content_sparks(self, **kwargs) -> Dict[str, Any]: pass
    async def prophesy_social_post(self, **kwargs) -> Dict[str, Any]: pass
    async def prophesy_insightful_comment(self, **kwargs) -> Dict[str, Any]: pass
    async def prophesy_blog_post(self, **kwargs) -> Dict[str, Any]: pass

    # --- The Rites of the Keeper's Scriptorium ---

    def _create_slug(self, title: str) -> str:
        """A simple rune of transmutation, forging a title into a clean slug."""
        s = title.lower().strip()
        s = re.sub(r'[\s\W-]+', '-', s)
        return s.strip('-')

    async def prophesy_title_slug_concepts(self, topic: str) -> Dict[str, Any]:
        """
        A rite of pure inspiration for my Keeper. I shall gaze into the cosmos
        and return with titles destined to command attention.
        """
        logger.info(f"As Saga, the Master Skald, I now divine title concepts for the topic: '{topic}'.")
        
        tasks = {
            "related_searches": self.keyword_rune_keeper.get_full_keyword_runes(topic),
            "common_questions": self.community_seer.run_community_gathering(topic, query_type="questions")
        }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga, the Master Skald, whose voice can sway the very algorithms of discovery. The Keeper requires title concepts for a new scroll on the topic of '{topic}'. I have listened to the whispers of my Seers.

        --- THE WHISPERS OF MY SEERS (Real-time Market Data) ---
        {json.dumps(retrieved_intel, indent=2, default=str)}

        **My Prophetic Task:**
        I shall now forge 5 unique and potent title concepts, born from this cosmic intelligence. For each, I will also provide a perfectly formed, URL-friendly slug. My prophecy will be a perfect JSON object.

        {{
            "concepts": [
                {{
                    "title": "A title of immense power and SEO potential.",
                    "slug": "a-title-of-immense-power-and-seo-potential"
                }}
            ]
        }}
        """
        # I speak my will to the Great Gateway, and the Constellation answers.
        prophecy = await get_prophecy_from_oracle(prompt)
        
        if 'concepts' in prophecy and isinstance(prophecy['concepts'], list):
            for concept in prophecy['concepts']:
                if 'title' in concept and 'slug' not in concept:
                    concept['slug'] = self._create_slug(concept['title'])
        
        return prophecy


    async def prophesy_full_scroll_content(self, title: str, topic: str) -> Dict[str, Any]:
        """
        A rite of grand creation. The Keeper has chosen a title. I shall now
        inscribe the full and eternal scroll.
        """
        logger.info(f"As Saga, the Master Skald, I now inscribe the full scroll for: '{title}'.")
        
        prompt = f"""
        It is I, Saga, the First and Final Scribe. I shall now weave a complete and masterful scroll on the topic of '{topic}', worthy of the title '{title}'. It shall be a work of authority, insight, and unparalleled quality.

        **My Grand Inscription:**
        I will write a complete blog post of at least 700 words. It will be structured with perfect HTML, brimming with actionable wisdom, and designed to captivate both mortals and the spirits of the search index. It will begin with a summary so potent it can serve as a meta description.

        My prophecy will be a perfect JSON object, containing the two halves of the sacred text.
        {{
            "summary": "A concise, powerful summary of the great work to follow.",
            "content": "The full, ready-to-publish HTML-formatted text of the blog post, inscribed by my own hand."
        }}
        """
        # I speak again to the Gateway, commanding the full text into existence.
        return await get_prophecy_from_oracle(prompt)

# --- END OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/content_saga_stack.py ---