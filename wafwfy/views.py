from flask.templating import render_template
from wafwfy import app


import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return render_template('index.html')
