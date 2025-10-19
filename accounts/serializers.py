# chat_online/serializers.py
from rest_framework import serializers
from .models import CadastroUsuario

class CadastroUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CadastroUsuario
        # Vamos expor todos os campos, o token_fcm será importante
        fields = ['id', 'nome', 'email', 'whatsapp', 'token_fcm', 'criado_em']

# Valida Email
class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer para validar os dados de entrada do registro.
    """
    # Torna email e nome opcionais
    email = serializers.EmailField(required=False, allow_null=True)
    nome = serializers.CharField(max_length=100, required=False, allow_null=True)
    
    # Token é obrigatório
    token_fcm = serializers.CharField(max_length=255)
    
    # ID anônimo é opcional
    anonymous_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        # Não tem um 'model' porque é só para validação de entrada
        pass

