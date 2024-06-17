from django.apps import AppConfig


class TernoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'terno'

    def ready(self):
        from . import receivers
