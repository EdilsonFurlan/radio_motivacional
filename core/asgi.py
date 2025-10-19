# core/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import chat_online.routing # Supondo que o app se chama 'chat_online'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Este é o roteador principal.
# Ele olha o tipo de conexão (HTTP ou WebSocket) e a direciona.
application = ProtocolTypeRouter({
    # Se for HTTP, usa a configuração padrão do Django.
    "http": get_asgi_application(),
    
    # Se for WebSocket, passa para o nosso roteador de WebSockets.
    "websocket": URLRouter(
        chat_online.routing.websocket_urlpatterns
    ),
})


