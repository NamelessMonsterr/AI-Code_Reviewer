from celery import Celery
from app.core.config import settings

celery = Celery(
    'ai_code_reviewer',
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_pool_restarts=True,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Auto-discover tasks
celery.autodiscover_tasks(['app.tasks'])