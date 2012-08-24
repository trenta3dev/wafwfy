from flask import render_template, jsonify
from wafwfy import app


import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/story/')
def story():
    from wafwfy.models import Story

    stories = Story.all()
    return jsonify(objects=list(stories))
