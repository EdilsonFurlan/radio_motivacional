from django.urls import path
from . import views

app_name = 'chat_online'

urlpatterns = [
  
    # Rotas Servidor
    path("envio/", views.tela_envio,name='tela_envio'),
    
    # Rotas de FCM
    path('enviar-grupo/', views.enviar_para_grupo, name='enviar_grupo'),
    path('enviar-mensagem/', views.enviar_mensagem_individual, name='enviar_mensagem'),
  
    
 

    path('chat/history/', views.chat_history, name='chat_history'),
    
    # ... e a sua rota de WebSocket já está em routing.py, o que é perfeito.



]
