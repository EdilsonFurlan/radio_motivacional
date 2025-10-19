from django.db import models

class VideoRecomendado(models.Model):
    titulo = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    thumbnail_url = models.URLField()
    ao_vivo = models.BooleanField(default=False)  #Campo novo
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
