from invisibleroads_macros.security import make_random_string
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from .exceptions import InvisibleRoadsRecordsError
from .libraries.cache import CachingQuery


Base = declarative_base()
DATABASE = scoped_session(sessionmaker(
    extension=ZopeTransactionExtension(), query_cls=CachingQuery))


def get_unique_instance(Class, id_length=16, retry_count=3):
    count = 0
    while count < retry_count:
        instance = Class(id=make_random_string(id_length))
        try:
            DATABASE.add(instance)
            DATABASE.flush()
        except IntegrityError:
            DATABASE.rollback()
        else:
            break
        count += 1
    else:
        raise InvisibleRoadsRecordsError(
            'could not get unique instance (%s)' % Class)
    return instance
