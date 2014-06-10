# DDTSS-Django - A Django implementation of the DDTP/DDTSS website
# Copyright (C) 2011 Martijn van Oosterhout <kleptog@svana.org>
# See LICENCE file for details.

import functools

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from django.conf import settings

Base = declarative_base()

Session = None

def get_db_session():
    # create a configured "Session" class
    global Session
    if not Session:
        db_engine = sqlalchemy.create_engine(URL(**settings.DDTP_DATABASE), echo=settings.DEBUG)
        Session = sessionmaker(bind=db_engine)
    # create a Session
    return Session()

def with_db_session(view):
    """ Decorator that provides a session argument and cleans up on return """
    @functools.wraps(view)
    def new_view(*args, **kwargs):
        try:
            session = get_db_session()
            return view(session, *args, **kwargs)
        finally:
            session.close()
    return new_view
