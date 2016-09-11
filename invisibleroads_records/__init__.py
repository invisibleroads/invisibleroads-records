import logging
import zope.sqlalchemy
from sqlalchemy import engine_from_config
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from invisibleroads_posts.libraries.cache import configure_cache

from .libraries.cache import CachingQuery, SQLALCHEMY_CACHE


LOG = logging.getLogger(__name__)
LOG.addHandler(logging.NullHandler())
DATABASE_CONNECTION_ERROR_MESSAGE = """\
could not access database

Is the database server running?
Did you run the initialization script?

invisibleroads initialize development.ini
invisibleroads initialize production.ini"""


def includeme(config):
    configure_cache(config, SQLALCHEMY_CACHE, 'server_cache.sqlalchemy.')
    configure_database(config)
    configure_views(config)


def configure_database(config):
    settings = config.registry.settings
    if 'sqlalchemy.url' not in settings:
        raise KeyError('sqlalchemy.url')
    database_engine = engine_from_config(settings, 'sqlalchemy.')
    config.add_request_method(
        lambda request: get_database_session(database_engine, request.tm),
        'database', reify=True)
    config.include('pyramid_tm')


def configure_views(config):
    config.add_view(handle_database_connection_error, context=OperationalError)


def get_database_session(database_engine, transaction_manager):
    DatabaseSession = sessionmaker(query_cls=CachingQuery)
    DatabaseSession.configure(bind=database_engine)
    database_session = DatabaseSession()
    zope.sqlalchemy.register(
        database_session, transaction_manager=transaction_manager)
    return database_session


def handle_database_connection_error(context, request):
    response = request.response
    response.status_int = 500
    LOG.error(DATABASE_CONNECTION_ERROR_MESSAGE)
    return response
