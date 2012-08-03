
class DefaultSettings:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://wafwfy@localhost/wafwfy'
    ADMINS = ['admin@wafwfy.ahref.eu', ]

    # celery configuration
    BROKER_URL = 'redis://localhost:6379/0'

    from datetime import timedelta
    CELERYBEAT_SCHEDULE = {
        'fetch_userstories': {
            'task': 'wafwfy.tasks.fetch_userstories',
            'schedule': timedelta(seconds=60),
            'args': ()
        },
    }
