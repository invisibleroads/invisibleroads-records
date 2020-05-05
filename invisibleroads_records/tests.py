import transaction
from pytest import fixture

from .models import (
    Base, define_get_database_session, get_database_engine,
    get_transaction_manager_session)


@fixture
def records_request(posts_request, records_config, database):
    records_request = posts_request
    records_request.db = database
    yield records_request


@fixture
def records_config(posts_config):
    posts_config.include('invisibleroads_records')
    yield posts_config


@fixture
def database(records_settings, database_extensions):
    database_engine = get_database_engine(records_settings)
    for Extension in database_extensions:
        Extension(records_settings).configure(database_engine)
    Base.metadata.create_all(database_engine)
    get_database_session = define_get_database_session(database_engine)
    database_session = get_transaction_manager_session(
        get_database_session, transaction.manager)
    yield database_session
    transaction.abort()
    Base.metadata.drop_all(database_engine)


@fixture
def database_extensions():
    return []


@fixture
def records_settings(posts_settings):
    posts_settings['sqlalchemy.url'] = 'sqlite://'
    yield posts_settings
