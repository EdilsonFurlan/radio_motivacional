from django.urls import path
from . import views
from .views import registrar_usuario, enviar_mensagem, tela_envio, enviar_para_grupo


urlpatterns = [
    path("registrar/", registrar_usuario),
    path("envio/", tela_envio),
    path("enviar-grupo/", enviar_para_grupo),
    path("enviar-mensagem/", enviar_mensagem),
    path("videos/", views.lista_videos_recomendados, name="videos_recomendados"),
]