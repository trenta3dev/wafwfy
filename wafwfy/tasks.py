from wafwfy import celery_instance


@celery_instance.task()
def fetch_userstories():
    """ fetch userstories from pivotaltracker and add some information
    into the database.
    """
    pass
