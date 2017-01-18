from invisibleroads_macros.security import make_random_string
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from sqlalchemy.types import String

from .exceptions import InvisibleRoadsRecordsError
from .libraries.cache import FromCache


NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


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
                'could not get unique record (%s)' % Class.__tablename__)
        return record

    @classmethod
    def get_from(Class, request):
        matchdict = request.matchdict
        database = request.database
        key = Class.__tablename__ + '_id'
        record_id = matchdict[key]
        record = Class.get(record_id, database)
        if not record:
            raise HTTPNotFound({key: 'bad'})
        return record

    @classmethod
    def get(Class, record_id, database):
        return database.query(Class).get(record_id)

    def __repr__(self):
        return '<%s(id=%s)>' % (self.__class__.__name__, self.id)


class CachedRecordMixin(RecordMixin):

    @classmethod
    def get(Class, record_id, database):
        if not record_id:
            return
        return Class._make_cache_query(record_id, database).get(record_id)

    @classmethod
    def clear_from_cache(Class, record_id, database):
        Class._make_cache_query(record_id, database).invalidate()

    @classmethod
    def _make_cache_query(Class, record_id, database):
        return database.query(Class).options(
            FromCache(cache_key='%s.id=%s' % (Class.__name__, record_id)))

    def update(self, database):
        database.add(self)
        self.__class__.clear_from_cache(self.id, database)
