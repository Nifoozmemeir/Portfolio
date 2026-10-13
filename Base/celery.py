import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Base.settingslocal')

app = Celery('Base')
app.config_from_object('django.conf:settings', namespace='CELERY') # Lee todos los CELERY_* de los settings
app.autodiscover_tasks() # Encuentra Base/Core/tasks.py solo
