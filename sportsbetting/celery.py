from celery.schedules import crontab

app.conf.beat_schedule = {
    'sync-nfl-scores-daily': {
        'task': 'sportsbetting.tasks.sync_nfl_scores',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}