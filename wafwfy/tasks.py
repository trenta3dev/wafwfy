from wafwfy import celery_instance, redis, app
from wafwfy.helpers import PivotalRequest
from wafwfy.models import Story, Iteration


@celery_instance.task()
def fetch_stories():
    """
    fetch userstories from pivotaltracker and add some information
    into the database.
    """
    redis.flushdb()

    request = PivotalRequest()
    pipe = redis.pipeline(transaction=True)

    for iteration in request.iter_iterations():
        iteration_id = iteration['id']
        Iteration.create(iteration, pipe=pipe)

        app.logger.info('Processing iteration: %s', iteration_id)

        for story in request.iter_stories(iteration['stories']):
            story_id = story['id']
            Story.create(story, pipe=pipe)
            Iteration.add_story(iteration_id, story_id, pipe=pipe)

            app.logger.info(story_id)

    app.logger.info('retrieve stories in the icebox')
    for story in request.iter_icebox():
        story_id = story['id']
        Story.create(story, pipe=pipe)

        app.logger.info(story_id)

    pipe.execute()
