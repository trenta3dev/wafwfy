import redis

RED = redis.StrictRedis()
CHANNEL_NAME = 'client_stream'


def event_stream():
    """ publisher/subscriber for sending events to client
    """
    pubsub = RED.pubsub()
    pubsub.subscribe(CHANNEL_NAME)
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']


def send_event(event):
    return RED.publish(CHANNEL_NAME, event)


def refresh_clients():
    return send_event('refresh')
