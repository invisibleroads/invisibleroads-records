import transaction
from pytest import fixture
from sqlalchemy import engine_from_config

from invisibleroads_records.models import Base, get_database_session


@fixture
def records_request(posts_request, config, database):
    config.include('invisibleroads_records')
    records_request = posts_request
    records_request.database = database
    yield records_request


@fixture
def database(database_engine):
    yield get_database_session(database_engine, transaction.manager)
    transaction.abort()


@fixture
def database_engine(settings):
    database_engine = engine_from_config(settings)
    Base.metadata.create_all(database_engine)
    yield database_engine
    Base.metadata.drop_all(database_engine)


@fixture
def settings(data_folder):
    return {
        'data.folder': data_folder,
        'sqlalchemy.url': 'sqlite:///:memory:',
    }
