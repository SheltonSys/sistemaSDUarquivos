from django.apps import AppConfig

class WebappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webapp'

    def ready(self):
        import webapp.signals  # garante que signals serão carregados corretamente
