wafwfy
======

we are "fortunately" working for you - a pivotaltracker monitor/dashboard to show everybody you're working really hard


howto
-----

Run the server with (it will be available at http://localhost:8000 ):
     
    python wafwfy/manage.py runserver --threaded

then run celery with:
     
    python wafwfy/manage.py celery