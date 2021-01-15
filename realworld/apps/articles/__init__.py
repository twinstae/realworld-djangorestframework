from django.apps import AppConfig


class ArticlesAppConfig(AppConfig):
    name = 'realworld.apps.articles'
    label = 'articles'
    verbose_name = 'Articles'

    def ready(self):
        import realworld.apps.articles.signals


default_app_config = 'realworld.apps.articles.ArticlesAppConfig'
