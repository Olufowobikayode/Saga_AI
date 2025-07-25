# --- START OF FILE backend/celery_app.py ---
import os
from celery import Celery
from dotenv import load_dotenv

# The worker must be made aware of the sacred runes in the .env scroll.
load_dotenv()

# We divine the location of the Redis message broker, the great nexus of tasks.
# It defaults to the local realm if no other is specified.
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# The Celery worker's consciousness is forged.
# We name it 'backend' so it knows its domain.
# We link it to Redis as both its 'broker' (where it receives tasks)
# and its 'backend' (where it stores the results of its prophecies).
celery_app = Celery(
    'backend',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['backend.tasks'] # We command it to seek its tasks in the 'tasks.py' scroll.
)

# A final configuration decree for robustness.
celery_app.conf.update(
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)

if __name__ == '__main__':
    celery_app.start()
# --- END OF FILE backend/celery_app.py ---