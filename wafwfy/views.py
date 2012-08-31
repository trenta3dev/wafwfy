import logging

from flask import render_template, jsonify
from flask.globals import request
from wafwfy import app


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


@app.route('/api/tags/')
def tags():
    from wafwfy.models import Story
    from collections import defaultdict

    stories = Story.all()
    tags = defaultdict(list)
    for story in stories:
        for label in story.get('labels', []):
            tags[label].append(story)
    return jsonify(objects=tags)


@app.route('/api/tags-count/')
def tags_count():
    from wafwfy.models import Story
    from collections import defaultdict

    stories = Story.all()
    tags = defaultdict(lambda:defaultdict(lambda: 0))
    for story in stories:
        print story
        for label in story.get('labels', []):
            tags[label][story['current_state']] += 1
    return jsonify(objects=tags)
