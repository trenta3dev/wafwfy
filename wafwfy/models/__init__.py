"""
A couple of models
"""
from flask import json
from wafwfy import redis, app


class BaseRedisModel(object):
    LIST_KEY = None
    ENTRY_KEY = None
    STATE_KEY = None

    PK_ATTRIB = 'id'
    STATE_ATTRIB = 'current_state'

    @classmethod
    def create(cls, a_dict, pipe=None):
        commit = False
        if pipe is None:
            pipe = redis.pipeline(transaction=True)
            commit = True

        the_id = a_dict[cls.PK_ATTRIB]

        the_key = cls.ENTRY_KEY.format(pk=the_id)

        pipe.delete(the_key)
        pipe.set(the_key, json.dumps(a_dict))
        pipe.rpush(cls.LIST_KEY, the_id)

        if cls.STATE_KEY and cls.STATE_ATTRIB:
            pipe.rpush(
                cls.STATE_KEY.format(state=a_dict[cls.STATE_ATTRIB]), the_id
            )

        if commit:
            pipe.execute()

    @classmethod
    def get(cls, id_):
        a_string = redis.get(cls.ENTRY_KEY.format(pk=id_))
        a_dict = json.loads(a_string)
        a_dict['id'] = id_

        return a_dict

    @classmethod
    def all(cls):
        ids = redis.lrange(cls.LIST_KEY, 0, -1)

        for id_ in ids:
            yield cls.get(id_)


class Story(BaseRedisModel):
    LIST_KEY = 'stories'
    ENTRY_KEY = 'story:{pk}'
    STATE_KEY = 'stories:{state}'


    @classmethod
    def current(cls):
        iter_ids = redis.lrange(
            Iteration.STATE_KEY.format(state='current'), 0, -1)

        for iter_id_ in iter_ids:
            ids = redis.smembers(Iteration.STORIES_LIST.format(pk=iter_id_))
            for id_ in ids:
                yield cls.get(id_)


    @classmethod
    def count_icebox(cls):
        return redis.scard(
            cls.STATE_KEY.format(
                state='unscheduled'
            )
        )

    @classmethod
    def iter_icebox(cls):
        ids = redis.smembers(
            cls.STATE_KEY.format(
                state='unscheduled'
            )
        )

        for id_ in ids:
            yield cls.get(id_)


class Iteration(BaseRedisModel):
    STORY_KEY = 'story:{pk}'
    LIST_KEY = 'iterations'
    ENTRY_KEY = 'iteration:{pk}'
    STATE_KEY = 'iterations:{state}'
    SCORE_LIST = 'iteration:{pk}:score'
    STORIES_LIST = 'iteration:{pk}:stories'
    INITIAL_VELOCITY = 15

    @classmethod
    def create(cls, a_dict, pipe=None):
        new_dict = dict(a_dict)
        new_dict.pop('stories')
        return super(Iteration, cls).create(new_dict, pipe=pipe)

    @classmethod
    def add_story(cls, iteration_id, story_id, pipe=None):
        commit = False
        if pipe is None:
            pipe = redis.pipeline(transaction=True)
            commit = True

        iteration_key = cls.STORIES_LIST.format(pk=iteration_id)
        pipe.sadd(iteration_key, story_id)

        if commit:
            pipe.execute()

    @classmethod
    #TODO current velocity = avg(last #3 iteration)
    #     iteration velocity = sum(
    def get_velocity_for_iteration(cls, iteration_id, with_team_strength=False):
        if iteration_id <= 0:
            return 0
        elif iteration_id == 1:
            return cls.INITIAL_VELOCITY

        stories_ids = redis.smembers(cls.STORIES_LIST.format(pk=iteration_id))
        team_strength = float(json.loads(
            redis.get(cls.ENTRY_KEY.format(pk=iteration_id)))['team_strength'])

        iteration_velocity = sum([
            json.loads(
                redis.get(cls.STORY_KEY.format(pk=pk))
            ).get('estimate', 0) for pk in stories_ids
        ])

        if with_team_strength:
            return int(iteration_velocity / team_strength)
        else:
            return iteration_velocity

    @classmethod
    def get_current_velocity(cls):
        current_iteration = cls.get_current()
        iteration_velocity = 0
        for i in range(3):
            iteration_velocity += cls.get_velocity_for_iteration(current_iteration - i - 1, True)

        return iteration_velocity/3

    @classmethod
    def get_current(cls):
        return int(redis.lindex(cls.STATE_KEY.format(state='current'), -1))
