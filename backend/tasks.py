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
        _engine_instance = SagaEngine()
    return _engine_instance

logger = logging.getLogger(__name__)

def run_async(coro):
    """A sacred vessel to run an asynchronous coroutine within a synchronous realm."""
    return asyncio.run(coro)

# --- The Sacred Tasks ---

@celery_app.task(bind=True, name="tasks.prophesy_grand_strategy")
def prophesy_grand_strategy_task(self, **kwargs: Any) -> Dict[str, Any]:
    logger.info(f"CELERY WORKER (Task ID: {self.request.id}): Grand Strategy task received for '{kwargs.get('interest')}'.")
    try:
        engine = get_engine()
        return run_async(engine.grand_strategy_stack.prophesy(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {self.request.id}): Grand Strategy task failed: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': 'The prophecy was disrupted.', 'details': str(e)})
        raise

@celery_app.task(bind=True, name="tasks.prophesy_new_venture_visions")
def prophesy_new_venture_visions_task(self, **kwargs: Any) -> Dict[str, Any]:
    logger.info(f"CELERY WORKER (Task ID: {self.request.id}): New Venture Visions task for '{kwargs.get('interest')}'.")
    try:
        engine = get_engine()
        return run_async(engine.new_ventures_stack.prophesy_initial_visions(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {self.request.id}): New Venture Visions task failed: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': 'The prophecy was disrupted.', 'details': str(e)})
        raise

@celery_app.task(bind=True, name="tasks.prophesy_venture_blueprint")
def prophesy_venture_blueprint_task(self, **kwargs: Any) -> Dict[str, Any]:
    logger.info(f"CELERY WORKER (Task ID: {self.request.id}): Venture Blueprint task received.")
    try:
        engine = get_engine()
        return run_async(engine.new_ventures_stack.prophesy_detailed_blueprint(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {self.request.id}): Venture Blueprint task failed: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': 'The prophecy was disrupted.', 'details': str(e)})
        raise

@celery_app.task(bind=True, name="tasks.prophesy_marketing_angles")
def prophesy_marketing_angles_task(self, **kwargs: Any) -> Dict[str, Any]:
    logger.info(f"CELERY WORKER (Task ID: {self.request.id}): Marketing Angles task for '{kwargs.get('product_name')}'.")
    try:
        engine = get_engine()
        return run_async(engine.marketing_saga_stack.prophesy_marketing_angles(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {self.request.id}): Marketing Angles task failed: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': 'The prophecy was disrupted.', 'details': str(e)})
        raise

@celery_app.task(bind=True, name="tasks.prophesy_marketing_asset")
def prophesy_marketing_asset_task(self, **kwargs: Any) -> Dict[str, Any]:
    logger.info(f"CELERY WORKER (Task ID: {self.request.id}): Marketing Asset task received.")
    try:
        engine = get_engine()
        return run_async(engine.marketing_saga_stack.prophesy_final_asset(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {self.request.id}): Marketing Asset task failed: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': 'The prophecy was disrupted.', 'details': str(e)})
        raise

@celery_app.task(bind=True, name="tasks.prophesy_pod_opportunities")
def prophesy_pod_opportunities_task(self, **kwargs: Any) -> Dict[str, Any]:
    logger.info(f"CELERY WORKER (Task ID: {self.request.id}): POD Opportunities task for '{kwargs.get('niche_interest')}'.")
    try:
        engine = get_engine()
        return run_async(engine.pod_saga_stack.prophesy_pod_opportunities(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {self.request.id}): POD Opportunities task failed: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': 'The prophecy was disrupted.', 'details': str(e)})
        raise

@celery_app.task(bind=True, name="tasks.prophesy_pod_package")
def prophesy_pod_package_task(self, **kwargs: Any) -> Dict[str, Any]:
    logger.info(f"CELERY WORKER (Task ID: {self.request.id}): POD Package task received.")
    try:
        engine = get_engine()
        return run_async(engine.pod_saga_stack.prophesy_pod_design_package(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {self.request.id}): POD Package task failed: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': 'The prophecy was disrupted.', 'details': str(e)})
        raise

@celery_app.task(bind=True, name="tasks.prophesy_commerce_saga")
def prophesy_commerce_saga_task(self, **kwargs: Any) -> Dict[str, Any]:
    prophecy_type = kwargs.get('prophecy_type')
    logger.info(f"CELERY WORKER (Task ID: {self.request.id}): Commerce Saga task for type '{prophecy_type}'.")
    try:
        engine = get_engine()
        return run_async(engine.commerce_saga_stack.prophesy_from_task_data(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {self.request.id}): Commerce Saga task failed: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': f"The Commerce Saga prophecy for '{prophecy_type}' was disrupted.", 'details': str(e)})
        raise

@celery_app.task(bind=True, name="tasks.prophesy_content_saga")
def prophesy_content_saga_task(self, **kwargs: Any) -> Dict[str, Any]:
    content_type = kwargs.get('content_type')
    logger.info(f"CELERY WORKER (Task ID: {self.request.id}): Content Saga task for type '{content_type}'.")
    try:
        engine = get_engine()
        return run_async(engine.content_saga_stack.prophesy_from_task_data(**kwargs))
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {self.request.id}): Content Saga task failed: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': f"The Content Saga prophecy for '{content_type}' was disrupted.", 'details': str(e)})
        raise
# --- END OF FILE backend/tasks.py ---