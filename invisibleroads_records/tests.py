import transaction
from invisibleroads_posts.tests import (
    application_config as posts_application_config,
    settings as posts_settings)
from pytest import fixture

from .models import (
    Base, define_get_database_session, get_database_engine,
    get_transaction_manager_session)


@fixture
def records_request(posts_request, application_config, db):
    records_request = posts_request
    records_request.db = db
    yield records_request


@fixture
def application_config(config):
    config = next(posts_application_config(config))
    config.include('invisibleroads_records')
    yield config


@fixture
def db(config):
    settings = config.get_settings()
    database_engine = get_database_engine(settings)
    Base.metadata.create_all(database_engine)
    get_database_session = define_get_database_session(database_engine)
    database_session = get_transaction_manager_session(
        get_database_session, transaction.manager)
    yield database_session
    transaction.abort()
    Base.metadata.drop_all(database_engine)


@fixture
def settings(data_folder):
    settings = next(posts_settings())
    settings['sqlalchemy.url'] = 'sqlite://'
    yield settings
