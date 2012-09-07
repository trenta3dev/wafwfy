import logging

from flask import render_template, jsonify, redirect
from wafwfy import app


# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route('/')
def index():
    from datetime import datetime
    from wafwfy.models import Iteration

    today = datetime.now()

    return render_template('index.html',
        epics=['one', 'two'],
        day=today.day,
        month=today.strftime("%B"),
        velocity=Iteration.get_current_velocity(),
    )


@app.route('/api/story/')
def story():
    from wafwfy.models import Story

    stories = Story.all()
    return jsonify(objects=list(stories))


@app.route('/api/current/')
def story_current():
    from wafwfy.models import Story

    stories = Story.current()
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
        for label in story.get('labels', []):
            tags[label][story['current_state']] += 1
    return jsonify(objects=tags)


@app.route('/avatar/<user>')
def avatar(user):
    from hashlib import md5

    email = md5(app.config['USER_EMAIL'].get(user, "")).hexdigest()

    return redirect(
        "https://secure.gravatar.com/avatar/{0}".format(email)
    )
