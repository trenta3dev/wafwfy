from wafwfy import celery_instance, redis, app
from wafwfy.helpers import PivotalRequest
from wafwfy.models import Story


@celery_instance.task()
def fetch_stories():
    """
    fetch userstories from pivotaltracker and add some information
    into the database.
    """
    request = PivotalRequest()
    pipe = redis.pipeline(transaction=True)

    for story in request.iter_stories():
        story_id = story['id']
        app.logger.info('Processing story: %s', story_id)

        Story.create(story, pipe=pipe)

    pipe.execute()
