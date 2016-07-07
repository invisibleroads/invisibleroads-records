import transaction
from importlib import import_module
from invisibleroads.scripts import ConfigurableScript
from pyramid.paster import bootstrap, setup_logging

from .models import Base


class RecordsScript(ConfigurableScript):

    priority = 20
    setting_name = ''

    def run(self, args):
        setup_logging(args.configuration_path)
        env = bootstrap(args.configuration_path)
        settings = env['registry'].settings
        if 'sqlalchemy.url' not in settings:
            return
        Base.metadata.create_all()
        setting_value = settings.get(
            'records.' + self.setting_name, '').strip()
        if not setting_value:
            return
        module_url, function_name = setting_value.rsplit('.', 1)
        module = import_module(module_url)
        function = getattr(module, function_name)
        function(env['request'])
        transaction.commit()


class InitializeRecordsScript(RecordsScript):

    setting_name = 'initialize'


class UpdateRecordsScript(RecordsScript):

    setting_name = 'update'
