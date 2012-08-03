import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskext.script import Manager, Server

from wafwfy import app

manager = Manager(app)


@manager.command
def create_db():
    from wafwfy.database import create_all
    create_all()


@manager.command
def drop_db():
    from wafwfy.database import drop_all
    drop_all()


@manager.command
def celery():
    import os
#    os.system('celery -A wafwfy.celery_instance beat --loglevel=info')
    os.system('celery -A wafwfy.celery_instance worker -B --loglevel=info')


manager.add_command('runserver',  Server(port=7998))


if __name__ == "__main__":
    manager.run()
