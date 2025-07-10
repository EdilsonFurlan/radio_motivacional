
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CadastroUsuario,VideoRecomendado
from .firebase import enviar_notificacao
from .firebase import enviar_para_varios 


@csrf_exempt
def registrar_usuario(request):
    if request.method == "POST":
        try:
            dados = json.loads(request.body)
            nome = dados.get("nome")
            email = dados.get("email")
            whatsapp = dados.get("whatsapp", "")
            token = dados.get("token")

            if not all([nome, email, token]):
                return JsonResponse({"status": "erro", "mensagem": "Campos obrigatórios ausentes"}, status=400)

            CadastroUsuario.objects.update_or_create(
                token_fcm=token,
                defaults={
                    "nome": nome,
                    "email": email,
                    "whatsapp": whatsapp,
                }
            )

            return JsonResponse({"status": "ok", "mensagem": "Usuário salvo"})

        except Exception as e:
            return JsonResponse({"status": "erro", "mensagem": str(e)}, status=500)

    return JsonResponse({"mensagem": "Método não permitido"}, status=405)


@csrf_exempt
def enviar_mensagem(request):
    if request.method == "POST":
        try:
            dados = json.loads(request.body)
            token = dados.get("token")
            titulo = dados.get("titulo")
            corpo = dados.get("corpo")

            if not all([token, titulo, corpo]):
                return JsonResponse({"status": "erro", "mensagem": "Campos obrigatórios ausentes"}, status=400)

            from .firebase import enviar_notificacao
            resposta = enviar_notificacao(token, titulo, corpo)

            return JsonResponse({"status": "ok", "resposta": resposta})

        except Exception as e:
            return JsonResponse({"status": "erro", "mensagem": str(e)}, status=500)

    return JsonResponse({"mensagem": "Método não permitido"}, status=405)

def tela_envio(request):
    usuarios = CadastroUsuario.objects.all()
    return render(request, "notificacoes/envio.html", {"usuarios": usuarios})

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

            from .firebase import enviar_para_varios
            resultados = enviar_para_varios(tokens, titulo, corpo, tipo=tipo, url=url)

            return JsonResponse({"status": "ok", "resultado": resultados})

        except Exception as e:
            return JsonResponse({"status": "erro", "mensagem": str(e)}, status=500)

    return JsonResponse({"mensagem": "Método não permitido"}, status=405)


def lista_videos_recomendados(request):
    videos = VideoRecomendado.objects.order_by('-criado_em')[:10]  # últimos 10
    data = [
        {
            "titulo": v.titulo,
            "url": v.url,
            "thumbnail": v.thumbnail_url,
            "ao_vivo": v.ao_vivo,
        }
        for v in videos
    ]
    return JsonResponse(data, safe=False)