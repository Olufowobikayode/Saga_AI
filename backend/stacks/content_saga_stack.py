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
# A comprehensive dictionary defining the nature of each social realm.
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
    "Threads": {"content_type": "Text", "primary_audience": "General / Conversational", "tone_and_style": "Conversational, text-based alternative to X, linked to Instagram audience. More casual than X."},
    "Quora": {"content_type": "Text", "primary_audience": "Q&A / General Knowledge", "tone_and_style": "Answering questions authoritatively. Well-structured, helpful answers can establish expertise."},
    
    # Messaging Platforms
    "WhatsApp": {"content_type": "Text", "primary_audience": "Private / Group Chat", "tone_and_style": "Direct messaging, status updates. Content should be highly personal or valuable for direct sharing in small groups."},
    "Facebook Messenger": {"content_type": "Text", "primary_audience": "Private / Chatbots", "tone_and_style": "Direct messaging, often used for customer service bots or close-knit group chats."},
    "Telegram": {"content_type": "Text", "primary_audience": "Private / Channels", "tone_and_style": "Broadcast channels and group chats. Good for building a dedicated community with updates and exclusive content."},
    "Signal": {"content_type": "Text", "primary_audience": "Private / Secure Chat", "tone_and_style": "Secure one-on-one or group messaging. Not a broadcast platform."},
    "WeChat": {"content_type": "Hybrid", "primary_audience": "Chinese Audience / Super-App", "tone_and_style": "All-in-one platform. Official Accounts for articles/updates, Moments for social sharing. Highly integrated ecosystem."},
    "KakaoTalk": {"content_type": "Hybrid", "primary_audience": "South Korean Audience", "tone_and_style": "Dominant messaging app in South Korea. Includes brand channels and social features."},
    "Viber": {"content_type": "Text", "primary_audience": "Private / Group Chat", "tone_and_style": "Messaging app similar to WhatsApp, popular in certain regions. Features channels and communities."},
    "Line": {"content_type": "Text", "primary_audience": "Asian Markets / Private Chat", "tone_and_style": "Popular messaging app in Japan, Thailand, Taiwan. Rich with stickers and brand accounts."},
    "Skype": {"content_type": "Hybrid", "primary_audience": "Professional / International Calls", "tone_and_style": "Primarily for video/voice calls, but has text messaging features. Used in business contexts."},
    
    # Visual & Creative Platforms
    "Snapchat": {"content_type": "Image", "primary_audience": "Younger Audience", "tone_and_style": "Ephemeral photos and short videos (Snaps). Authentic, behind-the-scenes, and immediate content works best."},
    "Behance": {"content_type": "Image", "primary_audience": "Creative Professionals (Design)", "tone_and_style": "High-quality portfolio platform for designers, illustrators, etc. Focus on showcasing detailed projects."},
    "DeviantArt": {"content_type": "Image", "primary_audience": "Artists / Fan Communities", "tone_and_style": "Broad art community. Showcase digital and traditional art. Very community-centric."},
    "Flickr": {"content_type": "Image", "primary_audience": "Photographers", "tone_and_style": "High-resolution photo sharing. Geared towards professional and amateur photographers to showcase their work."},
    "500px": {"content_type": "Image", "primary_audience": "Professional Photographers", "tone_and_style": "Portfolio site for professional photographers. Extremely high standard of quality."},
    "VSCO": {"content_type": "Image", "primary_audience": "Aesthetic / Photography", "tone_and_style": "Mobile-first photo sharing with a focus on high-quality filters and a curated aesthetic. Minimalist."},
    "BeReal": {"content_type": "Image", "primary_audience": "Gen Z / Close Friends", "tone_and_style": "Authentic, unedited snapshots taken at a specific time each day. Rejects polished, curated content."},
    "Lemon8": {"content_type": "Image", "primary_audience": "Lifestyle / Gen Z", "tone_and_style": "Visually rich, magazine-style posts about lifestyle, fashion, food. A mix of Instagram and Pinterest."},
    "MySpace": {"content_type": "Hybrid", "primary_audience": "Legacy / Music", "tone_and_style": "Legacy social network, now focused on music and entertainment. Highly customizable profiles."},

    # Video Platforms
    "Vimeo": {"content_type": "Video", "primary_audience": "Creative Professionals (Filmmakers)", "tone_and_style": "High-quality, artistic video hosting. Seen as the professional's YouTube. No ads, focus on quality."},
    "Twitch": {"content_type": "Video", "primary_audience": "Gaming / Live Streaming", "tone_and_style": "Live streaming platform, primarily for gaming, but expanding to other hobbies. Community interaction via chat is key."},
    "Rumble": {"content_type": "Video", "primary_audience": "Political / Free Speech", "tone_and_style": "Video platform with a focus on minimal content moderation, popular with political commentators."},
    "Douyin": {"content_type": "Video", "primary_audience": "Chinese Audience", "tone_and_style": "The Chinese counterpart to TikTok. Short-form video, highly advanced e-commerce integration."},
    "Kuaishou": {"content_type": "Video", "primary_audience": "Chinese Audience (Broader Demographics)", "tone_and_style": "Major competitor to Douyin in China, often with a focus on everyday life and broader demographics."},
    "Bilibili": {"content_type": "Video", "primary_audience": "Chinese Youth / ACG", "tone_and_style": "Chinese video platform focused on Anime, Comics, and Gaming (ACG). Features user-submitted commentary as scrolling on-screen text."},
    
    # Blogging & Writing Platforms
    "Medium": {"content_type": "Text", "primary_audience": "General / Tech / Business", "tone_and_style": "Long-form articles and essays. Clean, minimalist interface. Good for thought leadership."},
    "Substack": {"content_type": "Text", "primary_audience": "Niche Audiences / Writers", "tone_and_style": "Paid and free newsletter platform. Fosters a direct relationship between writer and reader."},
    "Tumblr": {"content_type": "Hybrid", "primary_audience": "Fandoms / Niche Blogs", "tone_and_style": "Micro-blogging platform with a strong emphasis on visual content and re-blogging (sharing). Highly community-driven."},
    "LiveJournal": {"content_type": "Text", "primary_audience": "Legacy / Niche Communities", "tone_and_style": "Older blogging platform with a focus on personal diaries and tight-knit communities."},

    # Interest-Based & Niche Networks
    "Goodreads": {"content_type": "Text", "primary_audience": "Readers / Book Lovers", "tone_and_style": "Social network for tracking reading, writing reviews, and discussing books."},
    "Letterboxd": {"content_type": "Text", "primary_audience": "Film Enthusiasts", "tone_and_style": "Social network for logging, reviewing, and discussing films."},
    "SoundCloud": {"content_type": "Audio", "primary_audience": "Musicians / Podcasters", "tone_and_style": "Audio hosting platform for emerging artists and podcasters to share their work."},
    "Last.fm": {"content_type": "Audio", "primary_audience": "Music Enthusiasts", "tone_and_style": "Music tracking and discovery service. Community is built around listening habits."},
    "Steam Community": {"content_type": "Hybrid", "primary_audience": "PC Gamers", "tone_and_style": "Social features built into the Steam gaming platform. Includes forums, reviews, and content sharing."},
    "ResearchGate": {"content_type": "Text", "primary_audience": "Academics / Researchers", "tone_and_style": "Social network for scientists and researchers to share papers, ask questions, and collaborate."},
    "Academia.edu": {"content_type": "Text", "primary_audience": "Academics / Researchers", "tone_and_style": "Platform for academics to share research papers."},
    "Yelp": {"content_type": "Text", "primary_audience": "Local Consumers", "tone_and_style": "Crowd-sourced reviews of local businesses."},
    "TripAdvisor": {"content_type": "Text", "primary_audience": "Travelers", "tone_and_style": "Reviews and booking for hotels, restaurants, and attractions."},
    "Nextdoor": {"content_type": "Text", "primary_audience": "Neighborhood Communities", "tone_and_style": "Hyper-local social network for neighborhoods. For local services and news."},
    "Clubhouse": {"content_type": "Audio", "primary_audience": "Professional / Niche Talks", "tone_and_style": "Live, drop-in audio conversations. Like a live, interactive podcast."},
    "Couchsurfing": {"content_type": "Hybrid", "primary_audience": "Budget Travelers / Cultural Exchange", "tone_and_style": "Community for travelers to find accommodation and connect with locals."},

    # Regional & Other Platforms
    "VK (VKontakte)": {"content_type": "Hybrid", "primary_audience": "Russian-speaking Audience", "tone_and_style": "Dominant social network in Russia, similar in functionality to Facebook."},
    "Odnoklassniki": {"content_type": "Hybrid", "primary_audience": "Russian-speaking Audience (Older)", "tone_and_style": "Popular social network in Russia and former Soviet republics, primarily for connecting with classmates."},
    "Xiaohongshu (Little Red Book)": {"content_type": "Image", "primary_audience": "Chinese Urban Youth / Lifestyle", "tone_and_style": "A blend of Instagram and Pinterest with a heavy focus on product reviews and lifestyle content. Highly influential for e-commerce."},
    "Weibo": {"content_type": "Hybrid", "primary_audience": "Chinese Audience", "tone_and_style": "Microblogging platform in China, similar to X but with more multimedia features."},
    "QQ": {"content_type": "Text", "primary_audience": "Chinese Audience", "tone_and_style": "Instant messaging platform in China, popular with younger users for social features and gaming."},
    "Xing": {"content_type": "Text", "primary_audience": "Professional Network (German-speaking)", "tone_and_style": "Professional networking site, similar to LinkedIn, with a strong user base in Germany, Austria, and Switzerland."},
    "Viadeo": {"content_type": "Text", "primary_audience": "Professional Network (France)", "tone_and_style": "French professional networking site, similar to LinkedIn."},
    "Mixi": {"content_type": "Hybrid", "primary_audience": "Japanese Audience", "tone_and_style": "One of Japan's first major social networks, focused on tight-knit communities and shared interests."},
    
    # Decentralized & Alternative Platforms
    "Mastodon": {"content_type": "Text", "primary_audience": "Tech-savvy / Decentralized", "tone_and_style": "Decentralized, open-source alternative to X. Consists of many independent servers (instances)."},
    "Bluesky": {"content_type": "Text", "primary_audience": "Tech-savvy / Ex-Twitter users", "tone_and_style": "Decentralized alternative to X, backed by Jack Dorsey."},
    "Gab": {"content_type": "Text", "primary_audience": "Political / Free Speech", "tone_and_style": "Social network with a strong emphasis on free speech, popular with conservative audiences."},
}

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
        """Phase 1: Generates 5 high-level, actionable content ideas ("sparks")."""
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
        
        # Manually add UUIDs to ensure uniqueness after generation
        if 'sparks' in prophecy and isinstance(prophecy['sparks'], list):
            for spark in prophecy['sparks']:
                spark['spark_id'] = str(uuid.uuid4())

        return {
            "sparks": prophecy.get("sparks", []),
            "retrieved_histories": retrieved_histories 
        }

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

        The Post I am commenting on (This is a mandatory context): "{post_to_comment_on}"

        My Own Related Content Idea (My Angle): {json.dumps(spark, indent=2)}
        My Promotional Link (Optional): {link or 'None'}
        My Link's Description: {link_description or 'None'}

        **Your Task:** Write an insightful comment.
        1.  **Add Value First:** Directly address the original post. Agree, disagree respectfully, or add a new perspective. Your comment must feel like a genuine contribution to the conversation.
        2.  **Bridge to Your Angle:** Smoothly transition to your own area of expertise (the "spark").
        3.  **Subtle Promotion (If Link Provided):** DO NOT just paste the link. Instead, allude to it.

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
        - **Structure:** Use clear headings, subheadings, lists, and bold text.
        - **Content:** Elaborate deeply on the spark's title and description.
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