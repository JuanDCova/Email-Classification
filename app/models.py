from django.db import models

# Create your models here.
from django.db import models

class Correo(models.Model):
    remitente = models.CharField(max_length=255)
    destinatario = models.CharField(max_length=255, null=True, blank=True)
    asunto = models.CharField(max_length=255)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.asunto

class ArchivoAdjunto(models.Model):
    correo = models.ForeignKey(Correo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='archivos_adjuntos/')

    def __str__(self):
        return self.nombre