from invisibleroads_macros.iterable import set_default
from invisibleroads_macros.log import get_log
from sqlalchemy import engine_from_config
from sqlalchemy.exc import OperationalError
from invisibleroads_posts import (
    InvisibleRoadsConfigurator, add_routes_for_fused_assets)
from invisibleroads_posts.libraries.cache import configure_cache

from .libraries.cache import SQLALCHEMY_CACHE
from .models import get_database_session, CLASS_REGISTRY


def main(global_config, **settings):
    config = InvisibleRoadsConfigurator(settings=settings)
    config.include('invisibleroads_posts')
    includeme(config)
    add_routes_for_fused_assets(config)
    return config.make_wsgi_app()


def includeme(config):
    configure_settings(config)
    configure_cache(config, SQLALCHEMY_CACHE, 'server_cache.sqlalchemy.')
    configure_database(config)
    configure_views(config)


def configure_settings(config, prefix='invisibleroads_records.'):
    settings = config.registry.settings
    set_default(
        settings, 'sqlalchemy.url', 'sqlite:///%s/database.sqlite' % settings[
            'data.folder'])
    for class_name, Class in CLASS_REGISTRY.items():
        if class_name.startswith('_'):
            continue
        set_default(settings, Class.__tablename__ + '.id.length', 32, int)


def configure_database(config):
    settings = config.registry.settings
    database_engine = engine_from_config(settings, 'sqlalchemy.')
    config.add_request_method(lambda request: get_database_session(
        database_engine, request.tm), 'database', reify=True)
    config.include('pyramid_tm')


def configure_views(config):
    config.add_view(handle_database_connection_error, context=OperationalError)


def handle_database_connection_error(context, request):
    response = request.response
    response.status_int = 500
    L.error(DATABASE_ERROR_MESSAGE % context)
    return response


L = get_log(__name__)
DATABASE_ERROR_MESSAGE = """%s

Did you run the initialization script?

invisibleroads initialize development.ini
invisibleroads initialize production.ini"""
