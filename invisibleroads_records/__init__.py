from sqlalchemy import engine_from_config
from invisibleroads_posts.libraries.cache import configure_cache

from .libraries.cache import SQLALCHEMY_CACHE
from .models import Base, DATABASE


def includeme(config):
    configure_cache(config, SQLALCHEMY_CACHE, 'server_cache.sqlalchemy.')
    configure_database(config)


def configure_database(config):
    settings = config.registry.settings
    if 'sqlalchemy.url' not in settings:
        raise KeyError('sqlalchemy.url')
    engine = engine_from_config(settings, 'sqlalchemy.')
    DATABASE.configure(bind=engine)
    Base.metadata.bind = engine
    config.include('pyramid_tm')
