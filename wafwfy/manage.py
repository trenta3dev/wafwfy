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
    fetch_stories(refresh_clients=True)


@manager.command
def refresh_clients():
    from wafwfy.events import refresh_clients
    refresh_clients()


manager.add_command('runserver',  Server(port=7998))


if __name__ == "__main__":
    manager.run()
