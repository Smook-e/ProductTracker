from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["worker.tasks"]
)

celery_app.conf.update(
    task_track_started=True,
    worker_prefetch_multiplier=1
)
# 🚀 ADD THE BEAT SCHEDULE HERE:
celery_app.conf.beat_schedule = {
    "auto-scrape-expired-products-every-5-minutes": {
        "task": "worker.tasks.check_expired_products", # Name of our task
        "schedule": 300.0, # Run every 300 seconds (5 minutes)
    },
}