from django.apps import AppConfig


class ChatOnlineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chat_online"
    label = "chat_online"      # <-- garante compatibilidade com migrações