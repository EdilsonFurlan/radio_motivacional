
from django.contrib import admin
from django.urls import path,include
from notificacoes import views
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/fcm/", include("notificacoes.urls")),
    path('teste/', views.teste_view, name='teste'),
]
