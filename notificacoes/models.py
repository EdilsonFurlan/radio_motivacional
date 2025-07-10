from django.db import models

class CadastroUsuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    token_fcm = models.CharField(max_length=255, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.email})"

class VideoRecomendado(models.Model):
    titulo = models.CharField(max_length=200)
    url = models.URLField()
    thumbnail_url = models.URLField()
    ao_vivo = models.BooleanField(default=False)  # 🔴 Campo novo
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo