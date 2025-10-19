
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import CadastroUsuario

from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .chat_memory import snapshot

import logging



@csrf_exempt
def enviar_mensagem_individual(request):
    if request.method == "POST":
        try:
            dados = json.loads(request.body)
            token = dados.get("token")
            titulo = dados.get("titulo")
            corpo = dados.get("corpo")

            if not all([token, titulo, corpo]):
                return JsonResponse({"status": "erro", "mensagem": "Campos obrigatórios ausentes"}, status=400)

            from notifications.firebase import enviar_notificacao
            resposta = enviar_notificacao(token, titulo, corpo)

            return JsonResponse({"status": "ok", "resposta": resposta})

        except Exception as e:
            return JsonResponse({"status": "erro", "mensagem": str(e)}, status=500)

    return JsonResponse({"mensagem": "Método não permitido"}, status=405)

def tela_envio(request):
    usuarios = CadastroUsuario.objects.all()
    return render(request, "chat_online/envio.html", {"usuarios": usuarios})

@csrf_exempt
def enviar_para_grupo(request):
    if request.method == "POST":
        try:
            dados = json.loads(request.body)
            tipo = dados.get("tipo")  # ex: "ao_vivo"
            titulo = dados.get("titulo")
            corpo = dados.get("corpo")
            url = dados.get("url")  # NÃO coloque default aqui

            print("📨 URL RECEBIDA:", url)  # ← GARANTE QUE O LINK CHEGOU

            if not all([tipo, titulo, corpo]):
                return JsonResponse({"status": "erro", "mensagem": "Dados incompletos"}, status=400)

            if tipo == "all":
                usuarios = CadastroUsuario.objects.all()
            elif tipo == "cadastrados":
                usuarios = CadastroUsuario.objects.exclude(nome__isnull=True).exclude(nome="")
            elif tipo == "nao_cadastrados":
                usuarios = CadastroUsuario.objects.filter(nome__isnull=True) | CadastroUsuario.objects.filter(nome="")
            elif tipo == "ao_vivo":
                usuarios = CadastroUsuario.objects.all()
            else:
                return JsonResponse({"status": "erro", "mensagem": "Tipo inválido"}, status=400)

            tokens = [u.token_fcm for u in usuarios if u.token_fcm]

            from notifications.firebase import enviar_para_varios
            resultados = enviar_para_varios(tokens, titulo, corpo, tipo=tipo, url=url)

            return JsonResponse({"status": "ok", "resultado": resultados})

        except Exception as e:
            return JsonResponse({"status": "erro", "mensagem": str(e)}, status=500)

    return JsonResponse({"mensagem": "Método não permitido"}, status=405)


# no topo do arquivo, importe a biblioteca de logging do Python

# ... suas outras importações

# Crie um "logger" para este arquivo
logger = logging.getLogger(__name__)

 


@api_view(['GET'])
def chat_history(request):
    return Response(snapshot(100))  # últimas 100 mensagens


