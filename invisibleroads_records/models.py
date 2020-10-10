from datetime import datetime
from invisibleroads_macros_log import get_timestamp
from invisibleroads_macros_security import make_random_string
from invisibleroads_posts.views import get_value
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import Column, engine_from_config
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.types import DateTime, String
from zope.sqlalchemy import register as register_transaction_listener

from .constants import NAMING_CONVENTION, RECORD_ID_LENGTH, RECORD_RETRY_COUNT
from .exceptions import InvisibleRoadsRecordsError
from .variables import RECORDS_REGISTRY


class RecordMixin(object):

    id = Column(String, primary_key=True)
    id_length = RECORD_ID_LENGTH

    @classmethod
    def make_unique_record(Class, database, retry_count=RECORD_RETRY_COUNT):
        count = 0
        id_length = Class.id_length
        while count < retry_count:
            record = Class(id=make_random_string(id_length))
            database.add(record)
            try:
                database.flush()
            except IntegrityError:
                database.rollback()
            else:
                break
            count += 1
        else:
            raise InvisibleRoadsRecordsError(
                f'could not get unique {Class.__tablename__}.id')
        return record

    @classmethod
    def get_from(Class, request, record_id=None):
        key = Class.__tablename__ + 'Id'
        if record_id is None:
            record_id = get_value(request, key)
        database = request.database
        record = Class.get(database, record_id)
        if not record:
            raise HTTPNotFound({key: 'bad'})
        return record

    @classmethod
    def get(Class, database, record_id):
        if record_id is None:
            return
        return database.query(Class).get(record_id)

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id})>'


class CreationMixin(object):

    creation_datetime = Column(DateTime, default=datetime.utcnow)

    @property
    def creation_timestamp(self):
        return get_timestamp(self.creation_datetime)


class ModificationMixin(object):

    modification_datetime = Column(DateTime, default=datetime.utcnow)

    @property
    def modification_timestamp(self):
        return get_timestamp(self.modification_datetime)


def get_database_engine(settings, prefix='sqlalchemy.'):
    engine = engine_from_config(settings, prefix)
    for DatabaseExtension in settings.get('database.extensions', []):
        DatabaseExtension(settings, prefix).configure(engine)
    return engine


def define_get_database_session(database_engine):
    get_database_session = sessionmaker()
    get_database_session.configure(bind=database_engine)
    return get_database_session


def get_transaction_manager_session(get_database_session, transaction_manager):
    database_session = get_database_session()
    register_transaction_listener(
        database_session, transaction_manager=transaction_manager)
    return database_session


metadata = Base = declarative_base(
    class_registry=RECORDS_REGISTRY,
    metadata=MetaData(naming_convention=NAMING_CONVENTION))
