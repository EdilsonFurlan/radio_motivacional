from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, CadastroUsuarioSerializer
from .models import CadastroUsuario

# Usuario/Accounts

@api_view(['POST'])
def registrar_ou_logar_usuario(request):
    """
    Esta API registra um novo usuário ou atualiza um existente.
    Usa o e-mail como identificador único.
    Se um token FCM já estiver em uso por outro e-mail, ele é "roubado" para o e-mail atual.
    """

    # --- PASSO 1: VALIDAÇÃO DOS DADOS DE ENTRADA ---
    # Usamos o UserRegistrationSerializer para garantir que os dados recebidos do app
    # (nome, email, token_fcm) são válidos antes de prosseguir.
    
    input_serializer = UserRegistrationSerializer(data=request.data)
    
    if not input_serializer.is_valid():
        # Se os dados não forem válidos (ex: e-mail em formato incorreto, campo faltando),
        # retorna um erro 400 com os detalhes do problema.
        print(f"Erro de validação no registro: {input_serializer.errors}")
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Se a validação passou, podemos usar os dados com segurança.
    validated_data = input_serializer.validated_data
    email = validated_data.get('email')
    nome = validated_data.get('nome')
    token_fcm = validated_data.get('token_fcm')

    # --- PASSO 2: LÓGICA DE NEGÓCIO E INTERAÇÃO COM O BANCO ---
    # Envolvemos tudo em um bloco try-except para capturar erros inesperados.

    try:
        # Lógica para garantir a unicidade do token FCM.
        # Encontra qualquer OUTRO usuário que tenha este token e define seu token como nulo.
        if token_fcm:
            CadastroUsuario.objects.filter(token_fcm=token_fcm).exclude(email__iexact=email).update(token_fcm=None)

        # A operação principal: encontrar um usuário pelo e-mail (ignorando maiúsculas/minúsculas)
        # e atualizar seus dados, ou criar um novo se ele não existir.
        usuario, created = CadastroUsuario.objects.update_or_create(
            email__iexact=email,
            defaults={
                'nome': nome,
                'email': email, # Garante que o email seja salvo com o case correto
                'token_fcm': token_fcm
            }
        )

        # --- PASSO 3: PREPARAR A RESPOSTA DE SUCESSO ---
        
        # Usamos o CadastroUsuarioSerializer para converter o objeto 'usuario' em JSON.
        output_serializer = CadastroUsuarioSerializer(usuario)

        # Define a mensagem de log e o status HTTP com base em se o usuário foi criado ou atualizado.
        if created:
            log_message = f"NOVO USUÁRIO CADASTRADO: {email}"
            status_code = status.HTTP_201_CREATED
        else:
            log_message = f"USUÁRIO EXISTENTE ATUALIZADO: {email}"
            status_code = status.HTTP_200_OK

        print(log_message)
        
        # Retorna os dados do usuário em JSON com o status code apropriado.
        return Response(output_serializer.data, status=status_code)

    except Exception as e:
        # --- PASSO 4: TRATAMENTO DE ERROS INESPERADOS ---
        
        # Se qualquer coisa der errado durante a operação com o banco de dados.
        print(f"ERRO INESPERADO AO REGISTRAR/LOGAR USUÁRIO '{email}': {e}")
        
        # Retorna uma mensagem de erro genérica para o app.
        return Response(
            {"erro": "Ocorreu um erro interno no servidor ao processar sua solicitação."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )