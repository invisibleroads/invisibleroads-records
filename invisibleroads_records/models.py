from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from .libraries.cache import CachingQuery


db = scoped_session(sessionmaker(
    extension=ZopeTransactionExtension(), query_cls=CachingQuery))
Base = declarative_base()
