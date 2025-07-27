# --- START OF REFACTORED FILE backend/tasks.py ---
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

# --- TIER 3 UPGRADE: Foundation for Real-Time Updates ---
def push_update_to_client(task_id: str, status: str, message: str, data: Any = None):
    """
    A placeholder for a future real-time update system (e.g., WebSockets).
    This function's responsibility is to send the progress of a task to the client.
    For now, it will simply log the action, but it establishes the pattern.
    
    In a real implementation, this would publish a message to a Redis Pub/Sub channel
    that the user's browser would be subscribed to via a WebSocket connection.
    """
    log_message = f"REAL-TIME UPDATE (Task ID: {task_id}): Status={status}, Message='{message}'"
    logger.info(log_message)
    # --- FUTURE IMPLEMENTATION ---
    # from backend.websockets import redis_pubsub
    # import json
    # update_payload = json.dumps({"task_id": task_id, "status": status, "message": message, "data": data})
    # redis_pubsub.publish(f"task_updates:{task_id}", update_payload)
    # ---------------------------

def run_async(coro):
    """A sacred vessel to run an asynchronous coroutine within a synchronous realm."""
    # This remains the same
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# --- The Sacred Tasks (Now with Real-Time Hooks) ---

def execute_prophecy_task(task_instance, prophecy_coroutine, task_name: str, **kwargs):
    """
    A standardized executor for all prophecy tasks to reduce code duplication
    and implement consistent real-time update hooks.
    """
    task_id = task_instance.request.id
    push_update_to_client(task_id, "STARTED", f"The {task_name} prophecy has begun...")
    
    try:
        engine = get_engine()
        # The actual RAG + LLM work is done here
        result = run_async(prophecy_coroutine(engine, **kwargs))
        push_update_to_client(task_id, "SUCCESS", f"The {task_name} prophecy is complete.", data=result)
        return result
    except Exception as e:
        logger.error(f"CELERY WORKER (Task ID: {task_id}): {task_name} task failed: {e}", exc_info=True)
        error_details = f"The {task_name} prophecy was disrupted. Details: {str(e)}"
        push_update_to_client(task_id, "FAILURE", error_details)
        # Re-raise the exception to let Celery know the task failed.
        # It will then be stored in the result backend.
        raise

# A helper coroutine must be defined for each Stack method
async def grand_strategy_coro(engine, **kwargs): return await engine.grand_strategy_stack.prophesy(**kwargs)
async def new_venture_visions_coro(engine, **kwargs): return await engine.new_ventures_stack.prophesy_initial_visions(**kwargs)
async def venture_blueprint_coro(engine, **kwargs): return await engine.new_ventures_stack.prophesy_detailed_blueprint(**kwargs)
async def marketing_angles_coro(engine, **kwargs): return await engine.marketing_saga_stack.prophesy_marketing_angles(**kwargs)
async def marketing_asset_coro(engine, **kwargs): return await engine.marketing_saga_stack.prophesy_final_asset(**kwargs)
async def pod_opportunities_coro(engine, **kwargs): return await engine.pod_saga_stack.prophesy_pod_opportunities(**kwargs)
async def pod_package_coro(engine, **kwargs): return await engine.pod_saga_stack.prophesy_pod_design_package(**kwargs)
async def commerce_saga_coro(engine, **kwargs): return await engine.commerce_saga_stack.prophesy_from_task_data(**kwargs)
async def content_saga_coro(engine, **kwargs): return await engine.content_saga_stack.prophesy_from_task_data(**kwargs)

# --- Refactored Task Definitions ---

@celery_app.task(bind=True, name="tasks.prophesy_grand_strategy")
def prophesy_grand_strategy_task(self, **kwargs: Any) -> Dict[str, Any]:
    return execute_prophecy_task(self, grand_strategy_coro, "Grand Strategy", **kwargs)

@celery_app.task(bind=True, name="tasks.prophesy_new_venture_visions")
def prophesy_new_venture_visions_task(self, **kwargs: Any) -> Dict[str, Any]:
    return execute_prophecy_task(self, new_venture_visions_coro, "New Venture Visions", **kwargs)

@celery_app.task(bind=True, name="tasks.prophesy_venture_blueprint")
def prophesy_venture_blueprint_task(self, **kwargs: Any) -> Dict[str, Any]:
    return execute_prophecy_task(self, venture_blueprint_coro, "Venture Blueprint", **kwargs)

@celery_app.task(bind=True, name="tasks.prophesy_marketing_angles")
def prophesy_marketing_angles_task(self, **kwargs: Any) -> Dict[str, Any]:
    return execute_prophecy_task(self, marketing_angles_coro, "Marketing Angles", **kwargs)

@celery_app.task(bind=True, name="tasks.prophesy_marketing_asset")
def prophesy_marketing_asset_task(self, **kwargs: Any) -> Dict[str, Any]:
    return execute_prophecy_task(self, marketing_asset_coro, "Marketing Asset", **kwargs)

@celery_app.task(bind=True, name="tasks.prophesy_pod_opportunities")
def prophesy_pod_opportunities_task(self, **kwargs: Any) -> Dict[str, Any]:
    return execute_prophecy_task(self, pod_opportunities_coro, "POD Opportunities", **kwargs)

@celery_app.task(bind=True, name="tasks.prophesy_pod_package")
def prophesy_pod_package_task(self, **kwargs: Any) -> Dict[str, Any]:
    return execute_prophecy_task(self, pod_package_coro, "POD Package", **kwargs)

@celery_app.task(bind=True, name="tasks.prophesy_commerce_saga")
def prophesy_commerce_saga_task(self, **kwargs: Any) -> Dict[str, Any]:
    return execute_prophecy_task(self, commerce_saga_coro, "Commerce Saga", **kwargs)

@celery_app.task(bind=True, name="tasks.prophesy_content_saga")
def prophesy_content_saga_task(self, **kwargs: Any) -> Dict[str, Any]:
    return execute_prophecy_task(self, content_saga_coro, "Content Saga", **kwargs)

# --- END OF REFACTORED FILE backend/tasks.py ---