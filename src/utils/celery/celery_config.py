from celery import Celery
from src.config import get_settings

settings = get_settings()

app = Celery(__name__, include=['src.utils.celery.celery_tasks'])
app.config_from_object(settings, namespace='CELERY')

# Queues storage if workers are busy
app.conf.broker_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

# Backend result storage
app.conf.result_backend = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

app.autodiscover_tasks()
