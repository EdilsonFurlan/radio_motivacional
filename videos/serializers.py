from rest_framework import serializers
from .models import VideoRecomendado

class VideoRecomendadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoRecomendado
        fields = ['id', 'titulo', 'url', 'thumbnail_url', 'ao_vivo']