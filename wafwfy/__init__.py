from flask import Flask

app = Flask(__name__)

app.config.from_object('wafwfy.settings.DefaultSettings')
app.config.from_envvar('WAFWFY_CONF', silent=True)
app.config.from_envvar('WAFWFY_EXTRA_CONF', silent=True)
app.config.from_pyfile('settings_local.py', silent=True)

app.config.setdefault('PIVOTAL_TOKEN', None)
app.config.setdefault('PIVOTAL_PROJECT', None)
app.config.setdefault('REDIS_STORY_KEY', 'story:{story_id}')
app.config.setdefault('REDIS_CURRENT_KEY', 'current')
app.config.setdefault('REDIS_STORIES_KEY', 'stories')
app.config.setdefault('REDIS_STORIES_STATE_KEY', 'stories:{state}')


if not app.debug and not app.testing:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app)

    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler('127.0.0.1',
                               'noreply@wafwfy.ahref.eu',
                               app.config['ADMINS'], 'wafwfy Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    file_handler = logging.FileHandler('/var/log/wafwfy/wafwfy.log')
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(
        file_handler
    )


# redis
from flask.ext.redis import Redis

redis = Redis()
redis.init_app(app)


# set up celery
from celery import Celery
celery_instance = Celery('wafwfy')
celery_instance.conf.add_defaults(app.config)
import wafwfy.tasks

# set up views
import wafwfy.views
