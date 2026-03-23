from django.apps import AppConfig


class AiCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_core'
    verbose_name = 'AI Ядро'

    def ready(self):
        # Подключаем сигналы для авто-обновления эмбеддингов
        import ai_core.signals  # noqa: F401
