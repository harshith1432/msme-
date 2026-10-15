"""
Celery Task Queue Configuration and Application Factory.
Gracefully supports eager synchronous execution when Redis/Celery is disabled or testing.
"""
import os
from celery import Celery

def make_celery(app=None):
    broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
    result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
    always_eager = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'true').lower() in ('true', '1')

    celery = Celery(
        'msme_tasks',
        broker=broker_url,
        backend=result_backend,
        include=[
            'backend.tasks.document_tasks',
            'backend.tasks.rag_tasks',
            'backend.tasks.generation_tasks'
        ]
    )

    celery.conf.update(
        task_always_eager=always_eager,
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Kolkata',
        enable_utc=True
    )

    if app:
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        celery.Task = ContextTask

    return celery

celery_app = make_celery()
