# --- START OF FILE backend/engine.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import iso3166
import uuid
import os

# --- Import all specialist knowledge sources (The Seers) ---
from backend.q_and_a import CommunitySaga
from backend.trends import TrendScraper
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.utils import get_prophecy_from_oracle

# --- Import the great Halls of Wisdom (The Stacks) ---
from backend.stacks.new_ventures_stack import NewVenturesStack
from backend.stacks.content_saga_stack import ContentSagaStack
from backend.stacks.grand_strategy_stack import GrandStrategyStack
from backend.stacks.marketing_saga_stack import MarketingSagaStack
from backend.stacks.pod_stack import PODSagaStack
from backend.stacks.commerce_saga_stack import CommerceSagaStack

# --- NEW: Import the scrolls for task delegation ---
from backend.tasks import (
    prophesy_grand_strategy_task,
    prophesy_new_venture_visions_task,
    prophesy_venture_blueprint_task,
    prophesy_marketing_angles_task,
    prophesy_marketing_asset_task,
    prophesy_pod_opportunities_task,
    prophesy_pod_package_task,
    prophesy_commerce_saga_task,
    prophesy_content_saga_task  # <-- CORRECTED: The import is now present
)


logger = logging.getLogger(__name__)

class SagaEngine:
    """
    The SagaEngine is the heart of the application. It now orchestrates the
    gathering of intelligence from its seers, knowing that the Stacks will
    draw their prophetic voice from the great Oracle Constellation.
    """
    _instance = None

    # Singleton pattern to ensure only one engine consciousness exists.
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SagaEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self, gemini_api_key: Optional[str] = None):
        # The __init__ guard ensures this complex setup runs only once.
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        logger.info("The SagaEngine awakens... The Constellation of Oracles is now my voice.")
        
        # This will load from .env if the key is not passed directly
        _gemini_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not _gemini_key:
            # In a containerized setup, env vars are king. Let's rely on them.
            # The API keys are loaded in the rotator, so we don't need to check here.
            pass

        seers = {
            'community_seer': CommunitySaga(),
            'trend_scraper': TrendScraper(),
            'keyword_rune_keeper': KeywordRuneKeeper(),
            'marketplace_oracle': GlobalMarketplaceOracle()
        }

        self.grand_strategy_stack = GrandStrategyStack(**seers)
        self.content_saga_stack = ContentSagaStack(**seers)
        self.new_ventures_stack = NewVenturesStack(**seers)
        self.marketing_saga_stack = MarketingSagaStack(**seers)
        self.pod_saga_stack = PODSagaStack(**seers)
        self.commerce_saga_stack = CommerceSagaStack(**seers)
        
        # This cache is now deprecated for multi-step prophecies.
        # We will keep it for now but the new flows should use the job results.
        self.strategy_session_cache = {}
        self._initialized = True
        logger.info("Saga is now fully conscious and ready to share her wisdom.")

    # Note: Helper methods like _get_user_tone_instruction and _resolve_country_context
    # will be moved inside the task logic as they are part of the prophecy itself.

    # --- NEW: The Rite of Delegation ---
    # The SagaEngine no longer performs prophecies. It commands the workers to do so.

    def delegate_grand_strategy(self, **kwargs) -> str:
        """Dispatches the Grand Strategy prophecy to a background Seer."""
        logger.info(f"SAGA ENGINE: Delegating Grand Strategy for '{kwargs.get('interest')}' to the Seers.")
        task = prophesy_grand_strategy_task.delay(**kwargs)
        return task.id

    def delegate_new_venture_visions(self, **kwargs) -> str:
        """Dispatches the New Ventures Visions prophecy to a background Seer."""
        logger.info(f"SAGA ENGINE: Delegating New Venture Visions for '{kwargs.get('interest')}' to the Seers.")
        task = prophesy_new_venture_visions_task.delay(**kwargs)
        return task.id
    
    def delegate_venture_blueprint(self, **kwargs) -> str:
        """Dispatches the Venture Blueprint prophecy to a background Seer."""
        logger.info(f"SAGA ENGINE: Delegating Venture Blueprint for session '{kwargs.get('venture_session_id')}' to the Seers.")
        task = prophesy_venture_blueprint_task.delay(**kwargs)
        return task.id

    def delegate_marketing_angles(self, **kwargs) -> str:
        """Dispatches the Marketing Angles prophecy to a background Seer."""
        logger.info(f"SAGA ENGINE: Delegating Marketing Angles for '{kwargs.get('product_name')}' to the Seers.")
        task = prophesy_marketing_angles_task.delay(**kwargs)
        return task.id

    def delegate_marketing_asset(self, **kwargs) -> str:
        """Dispatches the Marketing Asset prophecy to a background Seer."""
        logger.info(f"SAGA ENGINE: Delegating Marketing Asset for session '{kwargs.get('marketing_session_id')}' to the Seers.")
        task = prophesy_marketing_asset_task.delay(**kwargs)
        return task.id

    def delegate_pod_opportunities(self, **kwargs) -> str:
        """Dispatches the POD Opportunities prophecy to a background Seer."""
        logger.info(f"SAGA ENGINE: Delegating POD Opportunities for '{kwargs.get('niche_interest')}' to the Seers.")
        task = prophesy_pod_opportunities_task.delay(**kwargs)
        return task.id

    def delegate_pod_package(self, **kwargs) -> str:
        """Dispatches the POD Package prophecy to a background Seer."""
        logger.info(f"SAGA ENGINE: Delegating POD Package for session '{kwargs.get('pod_session_id')}' to the Seers.")
        task = prophesy_pod_package_task.delay(**kwargs)
        return task.id
    
    def delegate_commerce_saga(self, **kwargs) -> str:
        """Dispatches any Commerce Saga prophecy to a background Seer."""
        prophecy_type = kwargs.get('prophecy_type')
        logger.info(f"SAGA ENGINE: Delegating Commerce Saga of type '{prophecy_type}' to the Seers.")
        task = prophesy_commerce_saga_task.delay(**kwargs)
        return task.id

    def delegate_content_saga_task(self, **kwargs) -> str:
        """Dispatches any Content Saga prophecy to a background Seer."""
        content_type = kwargs.get('content_type')
        logger.info(f"SAGA ENGINE: Delegating Content Saga of type '{content_type}' to the Seers.")
        task = prophesy_content_saga_task.delay(**kwargs)
        return task.id

# --- END OF FILE backend/engine.py ---