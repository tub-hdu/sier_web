from celery import Celery

celery_app = Celery('mycelery')
celery_app.config_from_object('celery_task.config')