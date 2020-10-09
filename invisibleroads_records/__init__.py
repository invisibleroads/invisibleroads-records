from invisibleroads_macros_configuration import set_default
from invisibleroads_posts.routines.configuration import set_attribute

from .constants import RECORD_ID_LENGTH
from .models import (
    define_get_database_session,
    get_database_engine,
    get_transaction_manager_session)
from .variables import RECORDS_REGISTRY


def includeme(config):
    configure_settings(config)
    configure_models(config)


def configure_settings(config):
    settings = config.get_settings()
    set_attribute(
        settings, RECORDS_REGISTRY, 'id.length', RECORD_ID_LENGTH, int)
    set_default(
        settings, 'sqlalchemy.url',
        'sqlite:///%s/database.sqlite' % settings.get('data.folder', '.'))


def configure_models(config):
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'
    config.include('pyramid_tm')
    config.include('pyramid_retry')
    database_engine = get_database_engine(settings)
    get_database_session = define_get_database_session(database_engine)
    config.add_request_method(
        lambda r: get_transaction_manager_session(get_database_session, r.tm),
        'db', reify=True)
