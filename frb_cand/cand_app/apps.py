from django.apps import AppConfig


class CandAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cand_app'
    def ready(self):
        import cand_app.signals