import arrow
from datetime import datetime
from invisibleroads_macros.timestamp import get_timestamp
from invisibleroads_macros.security import make_random_string
from invisibleroads_posts.models import get_record_id
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError, engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.types import DateTime, String
from zope.sqlalchemy import register as register_transaction_listener

from .constants import RECORD_ID_LENGTH, RECORD_RETRY_COUNT
from .exceptions import InvisibleRoadsRecordsError
from .libraries.cache import CachingQuery, FromCache


CLASS_REGISTRY = {}
metaData = MetaData(naming_convention={
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
})
Base = declarative_base(class_registry=CLASS_REGISTRY, metadata=metaData)


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
                f'could not get unique {Class.__tablename__}')
        return record

    @classmethod
    def get_from(Class, request, record_id=None):
        key = Class.__tablename__ + '_id'
        if record_id is None:
            record_id = get_record_id(request, key)
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


class CachedRecordMixin(RecordMixin):

    @classmethod
    def get(Class, database, record_id):
        if record_id is None:
            return
        record = Class.query_cache(database, record_id).get(record_id)
        if record is not None:
            record = database.merge(record)
        return record

    @classmethod
    def clear_cache(Class, database, record_id):
        Class.query_cache(database, record_id).invalidate()

    @classmethod
    def query_cache(Class, database, record_id):
        return database.query(Class).options(FromCache(cache_key='%s.id=%s' % (
            Class.__name__, record_id)))

    def update_cache(self, database):
        self.__class__.clear_cache(database, self.id)


class CreationMixin(object):

    creation_datetime = Column(DateTime, default=datetime.utcnow)

    @property
    def creation_timestamp(self):
        return get_timestamp(self.creation_datetime)

    @property
    def creation_when(self):
        return arrow.get(self.creation_datetime).humanize()

    @classmethod
    def get_datetime(Class):
        return Class.creation_datetime


class ModificationMixin(object):

    modification_datetime = Column(DateTime)

    @property
    def modification_timestamp(self):
        return get_timestamp(self.modification_datetime)

    @property
    def modification_when(self):
        return arrow.get(self.modification_datetime).humanize()

    @classmethod
    def get_datetime(Class):
        return Class.modification_datetime


def includeme(config):
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'
    config.include('pyramid_tm')
    config.include('pyramid_retry')
    database_engine = get_database_engine(settings)
    get_database_session = define_get_database_session(database_engine)
    config.add_request_method(
        lambda r: get_transaction_manager_session(get_database_session, r.tm),
        'db', reify=True)


def get_database_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def define_get_database_session(database_engine):
    get_database_session = sessionmaker(query_cls=CachingQuery)
    get_database_session.configure(bind=database_engine)
    return get_database_session


def get_transaction_manager_session(get_database_session, transaction_manager):
    database_session = get_database_session()
    register_transaction_listener(
        database_session, transaction_manager=transaction_manager)
    return database_session
