# --- START OF FILE backend/stacks/content_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import uuid
import re

import google.generativeai as genai

from backend.keyword_engine import KeywordRuneKeeper
from backend.q_and_a import CommunitySaga
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

PLATFORM_NATURES = {
    # ... (This large dictionary remains unchanged)
}

class ContentSagaStack:
    """
    Saga's aspect as the Master Skald. It forges content for public users
    and now also serves as a high-speed writing assistant for the Admin's Grimoire.
    """
    def __init__(self, model: genai.GenerativeModel, **seers: Any):
        self.model = model
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.community_seer: CommunitySaga = seers['community_seer']

    # --- Methods for Public Users (remain unchanged) ---
    async def prophesy_content_sparks(self, tactical_interest: str, retrieved_histories: Dict[str, Any], link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        # ... (This method is for the main app and remains the same)
        pass
    async def prophesy_social_post(self, spark: Dict, platform: str, length: str, post_type: str, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        # ... (This method is for the main app and remains the same)
        pass
    async def prophesy_insightful_comment(self, spark: Dict, post_to_comment_on: str, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        # ... (This method is for the main app and remains the same)
        pass
    async def prophesy_blog_post(self, spark: Dict, link: Optional[str], link_description: Optional[str]) -> Dict[str, Any]:
        # ... (This method is for the main app and remains the same)
        pass


    # --- NEW: Methods for the Admin's Scriptorium ---

    def _create_slug(self, title: str) -> str:
        """Helper function to create a URL-friendly slug from a title."""
        s = title.lower().strip()
        s = re.sub(r'[\s\W-]+', '-', s)  # Replace spaces, non-word chars, and multiple dashes with a single dash
        return s.strip('-')

    async def prophesy_title_slug_concepts(self, topic: str) -> Dict[str, Any]:
        """
        (Admin Only) Performs a high-speed RAG to generate compelling blog post titles and slugs.
        """
        logger.info(f"CONTENT SAGA (ADMIN): Divining Title/Slug concepts for topic: '{topic}'")
        
        # High-speed RAG for title ideas
        tasks = {
            "related_searches": self.keyword_rune_keeper.get_full_keyword_runes(topic),
            "common_questions": self.community_seer.run_community_gathering(topic, query_type="questions")
        }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        You are an expert SEO copywriter and viral title generator. Your task is to generate 5 compelling, clickable, and SEO-friendly blog post titles based on a topic and real-time search data.

        --- TOPIC ---
        {topic}

        --- LIVE SEARCH INTELLIGENCE ---
        {json.dumps(retrieved_intel, indent=2, default=str)}

        **Your Task:**
        Generate 5 unique title concepts. For each concept, provide the title and a perfectly formatted, URL-friendly slug.

        Your output MUST be a valid JSON object with a single key "concepts", which is an array of objects:
        {{
            "concepts": [
                {{
                    "title": "A compelling, SEO-friendly title.",
                    "slug": "a-compelling-seo-friendly-title"
                }}
            ]
        }}
        """
        prophecy = await get_prophecy_from_oracle(self.model, prompt)
        
        # Ensure slugs are perfectly formatted as a fallback
        if 'concepts' in prophecy and isinstance(prophecy['concepts'], list):
            for concept in prophecy['concepts']:
                if 'title' in concept and 'slug' not in concept:
                    concept['slug'] = self._create_slug(concept['title'])
        
        return prophecy


    async def prophesy_full_scroll_content(self, title: str, topic: str) -> Dict[str, Any]:
        """
        (Admin Only) Takes a chosen title and generates the full summary and body content for a blog post.
        """
        logger.info(f"CONTENT SAGA (ADMIN): Generating full scroll content for title: '{title}'")
        
        prompt = f"""
        You are an expert long-form content writer and SEO specialist. Your task is to write a complete, well-structured, and insightful blog post based on the provided title and topic.

        --- CORE DIRECTIVE ---
        - Blog Post Title: {title}
        - General Topic: {topic}

        **Your Task:**
        Write a complete blog post of at least 700 words. The content should be valuable, authoritative, and engaging.
        - **Structure:** Use HTML tags for structure (<h2> for main headings, <h3> for subheadings, <p> for paragraphs, <ul> and <li> for lists, <strong> for bold text).
        - **Content:** Elaborate deeply on the title. Answer the underlying question thoroughly. Provide actionable advice and unique insights.
        - **Summary:** Begin with a concise, compelling summary that can be used as a meta description.

        Your output MUST be a valid JSON object with the following keys:
        {{
            "summary": "A short, SEO-friendly summary of the article (1-2 sentences).",
            "content": "The full, ready-to-publish HTML-formatted text of the blog post."
        }}
        """
        return await get_prophecy_from_oracle(self.model, prompt)

# --- END OF FILE backend/stacks/content_saga_stack.py ---