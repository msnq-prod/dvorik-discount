from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.include = [
    "app.tasks.broadcasts",
    "app.tasks.birthday",
    "app.tasks.reminders",
]
celery_app.conf.timezone = settings.TZ

celery_app.conf.beat_schedule = {
    "send-birthday-congrats": {
        "task": "tasks.send_birthday_congrats",
        "schedule": crontab(hour=9, minute=0),
    },
    "check-scheduled-broadcasts": {
        "task": "tasks.check_scheduled_broadcasts",
        "schedule": crontab(minute="*/1"),
    },
}
