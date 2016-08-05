from invisibleroads_macros.security import make_random_string
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from .exceptions import InvisibleRoadsRecordsError
from .libraries.cache import CachingQuery


db = scoped_session(sessionmaker(
    extension=ZopeTransactionExtension(), query_cls=CachingQuery))
Base = declarative_base()


def get_unique_instance(Class, id_length=16, retry_count=3):
    count = 0
    while count < retry_count:
        instance = Class(id=make_random_string(id_length))
        try:
            db.add(instance)
            db.flush()
        except IntegrityError as e:
            db.rollback()
        else:
            break
        count += 1
    else:
        raise InvisibleRoadsRecordsError(
            'could not get unique instance (%s)' % Class)
    return instance
