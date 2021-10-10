from django.apps import AppConfig


class ReflectionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mysite.reflections"

    def ready(self):
        from .signal_handlers import register_signal_handlers

        register_signal_handlers()
