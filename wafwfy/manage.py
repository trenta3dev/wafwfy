import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask.ext.script import Manager, Server

from wafwfy import app

manager = Manager(app)


@manager.command
def celery():
    import os
#    os.system('celery -A wafwfy.celery_instance beat --loglevel=info')
    os.system('celery -A wafwfy.celery_instance worker -B --loglevel=info')


@manager.command
def fetch_stories():
    from wafwfy.tasks import fetch_stories

    fetch_stories()


@manager.command
def flush_redis():
    from wafwfy import redis

    redis.flushdb()


@manager.command
def fetch_data():
    flush_redis()
    fetch_stories()


manager.add_command('runserver',  Server(port=7998))


if __name__ == "__main__":
    manager.run()
