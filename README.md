wafwfy
======

we are "fortunately" working for you - a pivotaltracker monitor/dashboard to show everybody you're working really hard


howto
-----

Run the server with (it will be available at http://localhost:8000 ):
     
    gunicorn --debug --worker-class=gevent -t 999999  wafwfy:app

then run celery with:
     
    python wafwfy/manage.py celery