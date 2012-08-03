from wafwfy import app


import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return '<h1>yay!</h1>'
