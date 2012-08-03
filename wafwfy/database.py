from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_all():
    from sqlalchemy.exc import ProgrammingError

    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling create_all()
    import wafwfy.models

    db.create_all()


def drop_all():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling drop_all()
    import wafwfy.models
    db.drop_all()
