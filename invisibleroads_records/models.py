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


class InstanceMixin(object):

    id = Column(String, primary_key=True, autoincrement=False)
    id_length = 32

    @classmethod
    def make_unique_instance(Class, database, id_length=None, retry_count=3):
        count = 0
        id_length = id_length or Class.id_length
        while count < retry_count:
            instance = Class(id=make_random_string(id_length))
            try:
                database.add(instance)
                database.flush()
            except IntegrityError:
                database.rollback()
            else:
                break
            count += 1
        else:
            raise InvisibleRoadsRecordsError(
                'could not get unique instance (%s)' % Class.__tablename__)
        return instance

    @classmethod
    def get_from(Class, request):
        matchdict = request.matchdict
        database = request.database
        key = Class.__tablename__ + '_id'
        instance_id = matchdict[key]
        instance = Class.get(instance_id, database)
        if not instance:
            raise HTTPNotFound({key: 'bad'})
        return instance

    @classmethod
    def get(Class, instance_id, database):
        return database.query(Class).get(instance_id)

    def __repr__(self):
        return '<%s(id=%s)>' % (self.__class__.__name__, self.id)


class CachedInstanceMixin(InstanceMixin):

    @classmethod
    def get(Class, instance_id, database):
        if not instance_id:
            return
        return Class._make_cache_query(instance_id, database).get(instance_id)

    @classmethod
    def clear_from_cache(Class, instance_id, database):
        Class._make_cache_query(instance_id, database).invalidate()

    @classmethod
    def _make_cache_query(Class, instance_id, database):
        return database.query(Class).options(
            FromCache(cache_key='%s.id=%s' % (Class.__name__, instance_id)))

    def update(self, database):
        database.add(self)
        self.__class__.clear_from_cache(self.id, database)
