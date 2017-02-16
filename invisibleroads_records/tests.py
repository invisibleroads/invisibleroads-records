import transaction
from pytest import fixture
from sqlalchemy import engine_from_config
from webtest import TestApp

from invisibleroads_records import main as get_app
from invisibleroads_records.models import Base, get_database_session


@fixture
def records_website(records_request):
    settings = records_request.registry.settings
    yield TestApp(get_app({}, **settings))


@fixture
def records_request(posts_request, website_config):
    settings = website_config.registry.settings
    database_engine = engine_from_config(settings)
    Base.metadata.create_all(database_engine)
    records_request = posts_request
    records_request.database = get_database_session(
        database_engine, transaction.manager)
    yield records_request
    transaction.abort()
    Base.metadata.drop_all(database_engine)


@fixture
def website_config(config):
    config.include('invisibleroads_posts')
    config.include('invisibleroads_records')
    yield config


@fixture
def settings(data_folder):
    return {
        'data.folder': data_folder,
        'sqlalchemy.url': 'sqlite:///:memory:',
    }
