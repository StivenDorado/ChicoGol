from django.contrib.auth.models import User
from django.db import models

from apps.equipos.models import Equipo
from apps.partidos.models import Partido


class SolicitudAmistad(models.Model):
    ESTADOS = [("pendiente", "Pendiente"), ("aceptada", "Aceptada"), ("rechazada", "Rechazada")]
    emisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="solicitudes_enviadas")
    receptor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="solicitudes_recibidas")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("emisor", "receptor"), name="unique_friend_request")]
        ordering = ("-creada_en",)


class ChatGrupo(models.Model):
    nombre = models.CharField(max_length=120)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=True, blank=True, related_name="chats")
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, null=True, blank=True, related_name="chats")
    miembros = models.ManyToManyField(User, related_name="chats", blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Mensaje(models.Model):
    chat = models.ForeignKey(ChatGrupo, on_delete=models.CASCADE, related_name="mensajes")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mensajes")
    texto = models.CharField(max_length=500)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("creado_en",)
