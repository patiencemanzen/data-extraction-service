# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_extraction_service.settings')

# Initialize Celery app
app = Celery('data_extraction_service')

# Configure Celery using Django's settings
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    broker_connection_retry_on_startup=True,
)

# Auto-discover tasks from installed apps
app.autodiscover_tasks()
