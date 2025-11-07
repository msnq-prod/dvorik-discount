from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.workers.broadcast"],
)

celery_app.conf.update(
    task_track_started=True,
)
