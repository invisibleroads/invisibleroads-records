from sqlalchemy import engine_from_config
from invisibleroads_posts.libraries.cache import configure_cache

from .libraries.cache import SQLALCHEMY_CACHE
from .models import Base, db


def includeme(config):
    configure_cache(config, SQLALCHEMY_CACHE, 'server_cache.sqlalchemy.')
    configure_database(config)


def configure_database(config):
    settings = config.registry.settings
    if 'sqlalchemy.url' not in settings:
        data_folder = settings['data.folder']
        settings['sqlalchemy.url'] = 'sqlite:///%s/db.sqlite' % data_folder
    engine = engine_from_config(settings, 'sqlalchemy.')
    db.configure(bind=engine)
    Base.metadata.bind = engine
    config.include('pyramid_tm')
