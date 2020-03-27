from invisibleroads.scripts import ConfigurableScript
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config

from .models import Base


class InitializeRecordsScript(ConfigurableScript):

    priority = 20

    def run(self, args):
        configuration_path = args.configuration_path
        setup_logging(configuration_path)
        settings = get_appsettings(configuration_path)
        database_engine = engine_from_config(settings)
        Base.metadata.create_all(database_engine)
