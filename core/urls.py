# core/urls.py
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include('inicio.urls')),
    path("admin/", admin.site.urls),
    path("api/", include("chat_online.urls")),
    path("videos/", include("videos.urls")),
    path('api/accounts/', include('accounts.urls')),
    path('painel/mensagens/', include('mensagem_voz.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
