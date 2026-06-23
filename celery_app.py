from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["worker.tasks", "worker.scheduler"]
)

celery_app.conf.update(
    task_track_started=True,
    worker_prefetch_multiplier=1
)

celery_app.conf.beat_schedule = {
    # Periodically refresh products whose next_scrape time has passed.
    "auto-scrape-expired-products-every-5-minutes": {
        "task": "worker.scheduler.check_expired_products",
        "schedule": 300.0,
    },
}