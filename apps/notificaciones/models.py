from django.contrib.auth.models import User
from django.db import models


class Notificacion(models.Model):
    TIPOS = [("partido", "Partido"), ("equipo", "Equipo"), ("social", "Social"), ("sistema", "Sistema")]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificaciones")
    tipo = models.CharField(max_length=20, choices=TIPOS, default="sistema")
    titulo = models.CharField(max_length=120)
    mensaje = models.CharField(max_length=240)
    url = models.CharField(max_length=240, blank=True)
    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("leida", "-creada_en")

    def __str__(self):
        return f"{self.usuario}: {self.titulo}"
