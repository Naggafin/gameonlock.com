import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gameonlock.settings.production")

app = Celery("gameonlock")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Periodic Task Setup
app.conf.beat_schedule = {
    "fetch_team_data_every_hour": {
        "task": "sportsbetting.tasks.fetch_and_store_team_data",
        "schedule": crontab(minute=0, hour="*/1"),  # Runs every hour
    },
}
