"""
Celery configuration file.

See https://docs.celeryq.dev/en/stable/userguide/configuration.html for available configuration properties.
"""
from datetime import timedelta
import os

from celery.schedules import crontab

# The task broker URL
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost")
# The result backend URL
backend_url = os.getenv("CELERY_BACKEND_URL", "redis://localhost")

# The periodic task schedule used by beat.
beat_schedule = {
    "data-scheduler-5s": {
        "task": "update_index",
        "schedule": timedelta(seconds=5),
    }
}

# List of modules containing tasks for workers to discover when started
include = [
    "bigse.celery.tasks",
]

task_routes = {"*": {"queue": "celery"}}
