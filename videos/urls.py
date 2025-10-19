from django.urls import path
from . import views

app_name = 'videos'
urlpatterns = [
    path('cadastrar/', views.cadastrar_video_view, name='cadastrar_video'),
    path('listar/', views.cadastrar_video_view, name='listar_videos'),
    # A API para o app
    path('api/', views.lista_videos_recomendados, name='api_videos'),
]