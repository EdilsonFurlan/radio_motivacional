from django.db import models

from django.utils import timezone
import uuid



    
class Mensagem_Voz_Audio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    text = models.TextField()
    file = models.FileField(upload_to="audios_db/")
    music_used = models.CharField(max_length=200, blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title