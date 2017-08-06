import arrow
from datetime import datetime
from invisibleroads_macros.security import make_random_string
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.types import DateTime, String
from zope.sqlalchemy import register as register_transaction_manager

from .exceptions import InvisibleRoadsRecordsError
from .libraries.cache import CachingQuery, FromCache


CLASS_REGISTRY = {}
NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(class_registry=CLASS_REGISTRY, metadata=metadata)


class RecordMixin(object):

    id = Column(String, primary_key=True, autoincrement=False)
    id_length = 32

    @classmethod
    def make_unique_record(Class, database, id_length=None, retry_count=3):
        count = 0
        id_length = id_length or Class.id_length
        while count < retry_count:
            record = Class(id=make_random_string(id_length))
            try:
                database.add(record)
                database.flush()
            except IntegrityError:
                database.rollback()
            else:
                break
            count += 1
        else:
            raise InvisibleRoadsRecordsError(
                'could not get unique record for ' + Class.__tablename__)
        return record

    @classmethod
    def get_from(Class, request, record_id=None):
        key = Class.__tablename__ + '_id'
        if not record_id:
            matchdict = request.matchdict
            record_id = matchdict[key]
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
        return '<%s(id=%s)>' % (self.__class__.__name__, self.id)


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
    def creation_when(self):
        return arrow.get(self.creation_datetime).humanize()


class ModificationMixin(object):

    modification_datetime = Column(DateTime)

    @property
    def modification_when(self):
        return arrow.get(self.modification_datetime).humanize()


def get_database_session(database_engine, transaction_manager):
    DatabaseSession = sessionmaker(query_cls=CachingQuery)
    DatabaseSession.configure(bind=database_engine)
    database_session = DatabaseSession()
    register_transaction_manager(
        database_session, transaction_manager=transaction_manager)
    return database_session
