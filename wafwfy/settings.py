from collections import OrderedDict


class DefaultSettings:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://wafwfy@localhost/wafwfy'
    ADMINS = ['admin@wafwfy.ahref.eu', ]

    # redis configuration
    REDIS_APP_DB = 0
    REDIS_CELERY_DB = 1

    # celery configuration
    BROKER_URL = 'redis://localhost:6379/{0}'.format(REDIS_CELERY_DB)

    from datetime import timedelta
    CELERYBEAT_SCHEDULE = {
        'fetch_stories': {
            'task': 'wafwfy.tasks.fetch_stories',
            'schedule': timedelta(minutes=60),
            'args': ()
        },
    }

    USER_EMAIL = {
        "Mattia Larentis": "mattialarentis@gmail.com",
        "Stefano Parmesan": "armisael.silix@gmail.com",
        "Martino Pizzol": "martino.pizzol@gmail.com",
        "Davide Setti": "davide.setti@gmail.com",
        "Michele Di Cosmo": "micheledicosmo@gmail.com",
    }

    EPICS = OrderedDict([
        ('FC-Flag', ['fc_flag']),
        ('FC-Stream', ['fc_stream']),
        ('wafwfy', ['wafwfy']),
        ('Progetto corriere.it', ['corriere']),
    ])