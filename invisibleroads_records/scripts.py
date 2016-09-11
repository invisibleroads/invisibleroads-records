import transaction
from invisibleroads.scripts import ConfigurableScript
from invisibleroads_macros.configuration import resolve_attribute
from pyramid.paster import bootstrap, setup_logging
from sqlalchemy import engine_from_config

from .models import Base


class RecordsScript(ConfigurableScript):

    priority = 20
    setting_name = ''

    def run(self, args):
        setup_logging(args.configuration_path)
        env = bootstrap(args.configuration_path)
        settings = env['registry'].settings
        # Update tables
        database_engine = engine_from_config(settings)
        Base.metadata.create_all(database_engine)
        # Resolve function
        function_spec = settings.get(
            'records.' + self.setting_name, '').strip()
        if not function_spec:
            return
        function = resolve_attribute(function_spec)
        # Update records
        with transaction.manager:
            function(env['request'])


class InitializeRecordsScript(RecordsScript):

    setting_name = 'initialize'


class UpdateRecordsScript(RecordsScript):

    setting_name = 'update'
