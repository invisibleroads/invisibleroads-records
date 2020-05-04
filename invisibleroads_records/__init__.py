from invisibleroads_macros_configuration import set_default

from .constants import RECORD_ID_LENGTH
from .models import CLASS_REGISTRY


def includeme(config):
    configure_settings(config)
    config.include('.models')


def configure_settings(config):
    settings = config.get_settings()
    for class_name, Class in CLASS_REGISTRY.items():
        if class_name.startswith('_'):
            continue
        key = Class.__tablename__ + '.id.length'
        value = set_default(settings, key, RECORD_ID_LENGTH, int)
        setattr(Class, 'id_length', value)
    set_default(
        settings, 'sqlalchemy.url',
        'sqlite:///%s/database.sqlite' % settings['data.folder'])
