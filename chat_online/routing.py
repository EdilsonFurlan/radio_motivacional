# chat_online/routing.py
from django.urls import path
from . import consumers

# Esta é a lista de rotas de WebSocket, similar ao urlpatterns.
websocket_urlpatterns = [
    path('ws/chat-ao-vivo/', consumers.PresencaConsumer.as_asgi()),
]