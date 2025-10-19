from django.urls import path
from . import views

app_name = 'mensagem_voz'

urlpatterns = [
    path('gerar/', views.gerar_mensagem_view, name='gerar_mensagem'),
]