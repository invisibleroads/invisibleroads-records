import transaction
from invisibleroads.scripts import ConfigurableScript
from invisibleroads_macros.configuration import resolve_attribute
from pyramid.paster import bootstrap, setup_logging

from .models import Base


class RecordsScript(ConfigurableScript):

    priority = 20
    setting_name = ''

    def run(self, args):
        setup_logging(args.configuration_path)
        env = bootstrap(args.configuration_path)
        Base.metadata.create_all()
        function_spec = env['registry'].settings.get(
            'records.' + self.setting_name, '').strip()
        if not function_spec:
            return
        function = resolve_attribute(function_spec)
        function(env['request'])
        transaction.commit()


class InitializeRecordsScript(RecordsScript):

    setting_name = 'initialize'


class UpdateRecordsScript(RecordsScript):

    setting_name = 'update'
