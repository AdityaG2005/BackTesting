from celery import Celery

celery_app = Celery(
    "backtesting_engine",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.core.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)