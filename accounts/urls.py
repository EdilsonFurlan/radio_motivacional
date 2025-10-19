# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('usuario/registrar/', views.registrar_ou_logar_usuario, name='api_registrar_usuario'),
]