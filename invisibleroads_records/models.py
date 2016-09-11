from invisibleroads_macros.security import make_random_string
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

from .exceptions import InvisibleRoadsRecordsError


NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
Base = declarative_base(
    metadata=MetaData(naming_convention=NAMING_CONVENTION))


def get_unique_instance(Class, database, id_length=16, retry_count=3):
    count = 0
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
            'could not get unique instance (%s)' % Class)
    return instance
