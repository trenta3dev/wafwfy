from wafwfy import celery_instance, redis, app
from wafwfy.helpers import PivotalRequest


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

        story_key = app.config['REDIS_STORY_KEY'].format(story_id=story_id)
        del story['id']

        pipe.delete(story_key)
        pipe.hmset(story_key, story)
        pipe.sadd(app.config['REDIS_STORIES_KEY'], story_id)
        pipe.sadd(
            app.config['REDIS_STORIES_STATE_KEY'].format(
                state=story['current_state']
            ),
            story_id
        )

    pipe.execute()
