from invisibleroads.scripts import ConfigurableScript
from pyramid.paster import bootstrap, setup_logging

from .models import Base, get_database_engine


class InitializeRecordsScript(ConfigurableScript):

    priority = 20

    def run(self, args):
        configuration_path = args.configuration_path
        setup_logging(configuration_path)
        with bootstrap(configuration_path) as env:
            request = env['request']
            settings = request.registry.settings
            database_engine = get_database_engine(settings)
        Base.metadata.create_all(database_engine)
