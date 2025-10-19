
from.models import VideoRecomendado
from django.shortcuts import render, redirect
import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import VideoRecomendadoSerializer


from django.http import JsonResponse
# Create your views here.

@api_view(['GET']) # Define que esta view só aceita requisições GET
def lista_videos_recomendados(request):
    """
    Retorna a lista de todos os vídeos recomendados,
    ordenados com os 'ao_vivo' primeiro, e depois por data de criação.
    """
    try:
        # 1. Busca os vídeos do banco de dados.
        #    A ordenação '-ao_vivo', '-criado_em' garante que:
        #    - Vídeos com 'ao_vivo=True' venham antes dos com 'ao_vivo=False'.
        #    - Dentro de cada grupo, os mais recentes venham primeiro.
        videos = VideoRecomendado.objects.order_by('-ao_vivo', '-criado_em')

        # 2. Usa o Serializer para converter a lista de objetos em dados prontos para JSON.
        #    'many=True' é crucial para listas de objetos.
        serializer = VideoRecomendadoSerializer(videos, many=True)

        # 3. Retorna os dados serializados usando a Response do DRF.
        return Response(serializer.data)

    except Exception as e:
        print(f"Erro ao buscar vídeos: {e}")
        # Retorna um erro 500 se algo der errado no servidor.
        return Response({"erro": "Não foi possível carregar os vídeos."}, status=500)
    






def extrair_video_id_youtube(url):
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

def cadastrar_video_view(request):
    error = None
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        url = request.POST.get('url', '').strip()
        ao_vivo = request.POST.get('ao_vivo') == 'on'

        if not titulo or not url:
            error = "Título e URL são obrigatórios."
        else:
            video_id = extrair_video_id_youtube(url)
            if video_id:
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                VideoRecomendado.objects.create(
                    titulo=titulo,
                    url=url,
                    ao_vivo=ao_vivo,
                    thumbnail_url=thumbnail_url
                )
                return redirect('listar_videos')
            else:
                error = "URL do YouTube inválida."

    videos = VideoRecomendado.objects.order_by('-criado_em')
    return render(request, 'videos/cadastrar_video.html', {'videos': videos, 'error': error})