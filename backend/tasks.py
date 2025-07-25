# --- START OF FILE backend/tasks.py ---
import logging
from typing import Dict, Any

from backend.celery_app import celery_app
from backend.engine import SagaEngine

# The keepers of state must be summoned only when the task is executed.
# This prevents circular dependencies and ensures the engine is ready.
_engine_instance: SagaEngine = None

def get_engine() -> SagaEngine:
    """
    A rite to summon the SagaEngine within the sacred realm of a Celery worker.
    This ensures the engine is initialized only once per worker process.
    """
    global _engine_instance
    if _engine_instance is None:
        # In a real production setup, GEMINI_API_KEY would be loaded from env vars here
        # For now, we assume the worker environment is configured like the main app.
        _engine_instance = SagaEngine(gemini_api_key="placeholder") # Key will be loaded by engine's __init__
    return _engine_instance

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.prophesy_grand_strategy")
def prophesy_grand_strategy_task(**kwargs: Any) -> Dict[str, Any]:
    """
    This is the sacred task, the echo of the original rite, now performed
    in the tranquil depths of a Celery worker, free from the haste of mortal requests.
    """
    logger.info(f"CELERY WORKER: A new Grand Strategy prophecy has been received for '{kwargs.get('interest')}'. The Seers are dispatched.")
    try:
        engine = get_engine()
        
        # The true invocation of the prophecy, now safely in the background.
        # We must use asyncio.run because Celery tasks are synchronous by default,
                # but our engine's heart beats to an asynchronous drum.
        import asyncio
        result = asyncio.run(engine.prophesy_grand_strategy(**kwargs))
        
        logger.info(f"CELERY WORKER: The Grand Strategy for '{kwargs.get('interest')}' has been forged.")
        return result
    except Exception as e:
        logger.error(f"CELERY WORKER: A catastrophic failure occurred during the Grand Strategy prophecy. Error: {e}", exc_info=True)
        # We return a structured error so the frontend can be notified of the failure.
        return {"error": "The prophecy was disrupted by a cosmic disturbance.", "details": str(e)}

# Note: We will add tasks for the other prophecies (New Ventures, Marketing, etc.) here in subsequent steps.
# --- END OF FILE backend/tasks.py ---