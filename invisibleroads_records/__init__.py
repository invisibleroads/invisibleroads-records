from invisibleroads_macros.configuration import set_default
from invisibleroads_macros.log import get_log
from invisibleroads_posts import (
    InvisibleRoadsConfigurator, add_routes_for_fused_assets)
from invisibleroads_posts.libraries.cache import configure_cache
from sqlalchemy.exc import OperationalError

from .constants import RECORD_ID_LENGTH
from .libraries.cache import SQLALCHEMY_CACHE
from .models import CLASS_REGISTRY


def main(global_config, **settings):
    config = InvisibleRoadsConfigurator(settings=settings)
    config.include('invisibleroads_posts')
    includeme(config)
    add_routes_for_fused_assets(config)
    return config.make_wsgi_app()


def includeme(config):
    configure_settings(config)
    configure_cache(config, SQLALCHEMY_CACHE, 'server_cache.sqlalchemy.')
    config.include('.models')
    configure_views(config)


def configure_settings(config, prefix='invisibleroads_records.'):
    settings = config.get_settings()
    set_default(
        settings, 'sqlalchemy.url', 'sqlite:///%s/database.sqlite' % settings[
            'data.folder'])
    for class_name, Class in CLASS_REGISTRY.items():
        if class_name.startswith('_'):
            continue
        key = Class.__tablename__ + '.id.length'
        value = set_default(settings, key, RECORD_ID_LENGTH, int)
        setattr(Class, 'id_length', value)


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
