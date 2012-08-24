"""
A couple of models
"""
from wafwfy import redis, app


class Story(object):
    @classmethod
    def create(cls, d_story, pipe=None):
        commit = False
        if pipe is None:
            pipe = redis.pipeline(transaction=True)
            commit = True

        story_id = d_story['id']

        story_key = app.config['REDIS_STORY_KEY'].format(story_id=story_id)
        del d_story['id']

        pipe.delete(story_key)
        pipe.hmset(story_key, d_story)
        pipe.sadd(app.config['REDIS_STORIES_KEY'], story_id)
        pipe.sadd(
            app.config['REDIS_STORIES_STATE_KEY'].format(
                state=d_story['current_state']
            ),
            story_id
        )

        if commit:
            pipe.execute()

    @classmethod
    def get(cls, id_):
        story = redis.hgetall(
            app.config['REDIS_STORY_KEY'].format(story_id=id_)
        )
        story['id'] = id_

        return story

    @classmethod
    def all(cls):
        ids = redis.smembers(app.config['REDIS_STORIES_KEY'])

        for id_ in ids:
            yield cls.get(id_)

    @classmethod
    def count_icebox(cls):
        return redis.scard(
            app.config['REDIS_STORIES_STATE_KEY'].format(
                state='unscheduled'
            )
        )

    @classmethod
    def iter_icebox(cls):
        ids = redis.smembers(
            app.config['REDIS_STORIES_STATE_KEY'].format(
                state='unscheduled'
            )
        )

        for id_ in ids:
            yield cls.get(id_)
