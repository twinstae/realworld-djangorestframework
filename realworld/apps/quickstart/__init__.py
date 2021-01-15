from django.apps import AppConfig


class QuickstartConfig(AppConfig):
    name = 'realworld.apps.quickstart'
    label = 'quickstart'
    verbose_name = 'Quickstart'


default_app_config = 'realworld.apps.quickstart.QuickstartConfig'
