import logging
import flask

from flask import render_template, jsonify, redirect
from wafwfy import app


# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route('/')
def index():
    from datetime import datetime
    from wafwfy.models import Iteration
    from wafwfy.helpers import calculate_team_percentages

    today = datetime.now()
    velocity = Iteration.get_current_velocity()
    completed, total = Iteration.get_current_points()
    strength = float(Iteration.get_current_strength())
    team_percentages = calculate_team_percentages(strength)

    return render_template('index.html',
        epics=app.config.get('EPICS').keys(),
        day=today.day,
        month=today.strftime("%B"),
        velocity=velocity,
        team_strength=team_percentages,
        completed_points=completed,
        total_points=int(velocity * strength),
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


@app.route('/api/velocity/<int:id>/')
def velocity_for_iteraction(id):
    from wafwfy.models import Iteration
    return jsonify(object=Iteration.get_velocity_for_iteration(id))


@app.route('/api/velocity/last/<int:num>/')
def velocity_for_n_iteractions(num):
    from wafwfy.models import Iteration
    all_velocity = []
    current_iteration = Iteration.get_current()
    for i in range(num):
        all_velocity.append(Iteration.get_velocity_for_iteration(current_iteration-i-1))
    all_velocity.reverse()
    return jsonify(object=all_velocity)


@app.route('/api/velocity/')
def current_velocity():
    from wafwfy.models import Iteration
    return jsonify(object=Iteration.get_current_velocity())


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


@app.route('/api/epics/')
def tags_count():
    from wafwfy.models import Story
    from collections import defaultdict

    stories = Story.all()

    # build a mapping tag -> id of the epic
    epics = app.config.get('EPICS')
    tag_to_id = {}
    for cnt, epic_label in enumerate(epics):
        for tag in epics[epic_label]:
            tag_to_id[tag] = cnt

    tags = defaultdict(lambda:defaultdict(lambda: 0))
    for story in stories:
        for label in story.get('labels', []):
            if label not in tag_to_id:
                continue
            tags[tag_to_id[label]][story['current_state']] += \
                story.get('estimate', 0.5)
    return jsonify(objects=tags)


@app.route('/avatar/<user>')
def avatar(user):
    from hashlib import md5

    email = md5(app.config['USER_EMAIL'].get(user, "")).hexdigest()

    return redirect(
        "https://secure.gravatar.com/avatar/{0}".format(email)
    )


@app.route('/stream')
def stream():
    """ SSE commands for each client
    """
    from  wafwfy.events import event_stream
    return flask.Response(event_stream(), mimetype="text/event-stream")
