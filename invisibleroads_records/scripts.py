from invisibleroads.scripts import ConfigurableScript
from invisibleroads_posts.routines.configuration import (
    load_bootstrapped_settings)

from .models import Base, get_database_engine


class InitializeRecordsScript(ConfigurableScript):

    priority = 20

    def run(self, args, argv):
        settings = load_bootstrapped_settings(args.configuration_path)
        if 'sqlalchemy.url' not in settings:
            return
        database_engine = get_database_engine(settings)
        Base.metadata.create_all(database_engine)
