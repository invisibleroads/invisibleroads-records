import transaction
from pyramid import testing
from pytest import fixture

from .models import (
    Base,
    define_get_database_session,
    get_database_engine,
    get_transaction_manager_session)


@fixture
def records_request(records_config, database, data_folder):
    request = testing.DummyRequest(
        db=database,
        data_folder=data_folder)
    request.json_body = {}
    yield request


@fixture
def records_config(records_settings):
    config = testing.setUp(settings=records_settings)
    config.include('invisibleroads_posts')
    config.include('invisibleroads_records')
    yield config
    testing.tearDown()


@fixture
def records_settings(posts_settings):
    records_settings = posts_settings
    records_settings['sqlalchemy.url'] = 'sqlite://'
    yield records_settings


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
