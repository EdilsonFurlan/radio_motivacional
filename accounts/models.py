from django.db import models

import uuid


class CadastroUsuario(models.Model):
    # Torna 'nome' opcional
    nome = models.CharField(max_length=100, blank=True, null=True)
    
    # 'email' pode ser nulo, mas se existir, deve ser único
    email = models.EmailField(unique=True, blank=True, null=True)
    
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    
    # O token não precisa ser único, mas o ID anônimo sim
    token_fcm = models.CharField(max_length=255, null=True, blank=True)
    
    # 👇 O CAMPO QUE FALTAVA 👇
    anonymous_id = models.UUIDField(unique=True, null=True, blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome or self.email or str(self.anonymous_id)}"
