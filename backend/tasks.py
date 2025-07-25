# --- START OF FILE backend/tasks.py ---
import logging
import asyncio
from typing import Dict, Any

from backend.celery_app import celery_app
from backend.engine import SagaEngine

# The keepers of state must be summoned only when the task is executed.
_engine_instance: SagaEngine = None

def get_engine() -> SagaEngine:
    """A rite to summon the SagaEngine within the sacred realm of a Celery worker."""
    global _engine_instance
    if _engine_instance is None:
        # The SagaEngine is now a Singleton, so this safely initializes it once per worker.
        _engine_instance = SagaEngine()
    return _engine_instance

logger = logging.getLogger(__name__)

# --- Helper for running async methods in sync Celery tasks ---
def run_async(func):
    return asyncio.run(func)

# --- The Sacred Tasks ---

@celery_app.task(name="tasks.prophesy_grand_strategy")
def prophesy_grand_strategy_task(**kwargs: Any) -> Dict[str, Any]:
    """The Grand Strategy prophecy, performed in the background."""
    logger.info(f"CELERY WORKER: Grand Strategy task received for '{kwargs.get('interest')}'.")
    try:
        engine = get_engine()
        # The engine's async method is now called here.
        return run_async(engine.grand_strategy_stack.prophesy_from_task_data(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER: Grand Strategy task failed: {e}", exc_info=True)
        return {"error": "The prophecy was disrupted.", "details": str(e)}

@celery_app.task(name="tasks.prophesy_new_venture_visions")
def prophesy_new_venture_visions_task(**kwargs: Any) -> Dict[str, Any]:
    """The New Venture Visions prophecy, performed in the background."""
    logger.info(f"CELERY WORKER: New Venture Visions task received for '{kwargs.get('interest')}'.")
    try:
        engine = get_engine()
        return run_async(engine.new_ventures_stack.prophesy_initial_visions_from_task_data(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER: New Venture Visions task failed: {e}", exc_info=True)
        return {"error": "The prophecy was disrupted.", "details": str(e)}

@celery_app.task(name="tasks.prophesy_venture_blueprint")
def prophesy_venture_blueprint_task(**kwargs: Any) -> Dict[str, Any]:
    """The Venture Blueprint prophecy, performed in the background."""
    logger.info(f"CELERY WORKER: Venture Blueprint task received.")
    try:
        engine = get_engine()
        return run_async(engine.new_ventures_stack.prophesy_detailed_blueprint_from_task_data(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER: Venture Blueprint task failed: {e}", exc_info=True)
        return {"error": "The prophecy was disrupted.", "details": str(e)}

@celery_app.task(name="tasks.prophesy_marketing_angles")
def prophesy_marketing_angles_task(**kwargs: Any) -> Dict[str, Any]:
    """The Marketing Angles prophecy, performed in the background."""
    logger.info(f"CELERY WORKER: Marketing Angles task received for '{kwargs.get('product_name')}'.")
    try:
        engine = get_engine()
        return run_async(engine.marketing_saga_stack.prophesy_marketing_angles(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER: Marketing Angles task failed: {e}", exc_info=True)
        return {"error": "The prophecy was disrupted.", "details": str(e)}

@celery_app.task(name="tasks.prophesy_marketing_asset")
def prophesy_marketing_asset_task(**kwargs: Any) -> Dict[str, Any]:
    """The Marketing Asset prophecy, performed in the background."""
    logger.info(f"CELERY WORKER: Marketing Asset task received.")
    try:
        engine = get_engine()
        return run_async(engine.marketing_saga_stack.prophesy_final_asset_from_task_data(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER: Marketing Asset task failed: {e}", exc_info=True)
        return {"error": "The prophecy was disrupted.", "details": str(e)}

@celery_app.task(name="tasks.prophesy_pod_opportunities")
def prophesy_pod_opportunities_task(**kwargs: Any) -> Dict[str, Any]:
    """The POD Opportunities prophecy, performed in the background."""
    logger.info(f"CELERY WORKER: POD Opportunities task received for '{kwargs.get('niche_interest')}'.")
    try:
        engine = get_engine()
        return run_async(engine.pod_saga_stack.prophesy_pod_opportunities(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER: POD Opportunities task failed: {e}", exc_info=True)
        return {"error": "The prophecy was disrupted.", "details": str(e)}

@celery_app.task(name="tasks.prophesy_pod_package")
def prophesy_pod_package_task(**kwargs: Any) -> Dict[str, Any]:
    """The POD Package prophecy, performed in the background."""
    logger.info(f"CELERY WORKER: POD Package task received.")
    try:
        engine = get_engine()
        return run_async(engine.pod_saga_stack.prophesy_pod_package_from_task_data(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER: POD Package task failed: {e}", exc_info=True)
        return {"error": "The prophecy was disrupted.", "details": str(e)}

@celery_app.task(name="tasks.prophesy_commerce_saga")
def prophesy_commerce_saga_task(**kwargs: Any) -> Dict[str, Any]:
    """The Commerce Saga prophecy, performed in the background."""
    prophecy_type = kwargs.get('prophecy_type')
    logger.info(f"CELERY WORKER: Commerce Saga task received for type '{prophecy_type}'.")
    try:
        engine = get_engine()
        return run_async(engine.commerce_saga_stack.prophesy_from_task_data(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER: Commerce Saga task failed: {e}", exc_info=True)
        return {"error": "The prophecy was disrupted.", "details": str(e)}

# --- END OF FILE backend/tasks.py ---