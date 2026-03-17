"""
Celery app configuration.
Broker: Redis
Result backend: Redis
Queues: critical (single screens), default (regular batches), bulk (500+)
"""

from celery import Celery
from kombu import Queue
# pyright: reportMissingImports=false, reportMissingModuleSource=false
from app.config import settings

celery_app = Celery(
    "hiresignal",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,
    task_time_limit=3600,
    task_soft_time_limit=3300,
)

celery_app.conf.include = [
    "app.workers.tasks.screening",
]

celery_app.autodiscover_tasks(["app.workers.tasks"])

celery_app.conf.task_queues = (
    Queue('critical', routing_key='critical'),
    Queue('default', routing_key='default'),
    Queue('bulk', routing_key='bulk'),
)

celery_app.conf.task_routes = {
    'app.workers.tasks.screening.process_single_resume': {'queue': 'critical'},
    'app.workers.tasks.screening.process_screening_job': {'queue': 'default'},
}
