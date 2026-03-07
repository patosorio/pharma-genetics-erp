from django.apps import AppConfig


class CultivationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cultivation'

    def ready(self):
        import cultivation.signals  # noqa: F401
