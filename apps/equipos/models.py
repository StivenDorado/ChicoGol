from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


class Equipo(models.Model):
    NIVELES = [("recreativo", "Recreativo"), ("intermedio", "Intermedio"), ("competitivo", "Competitivo")]
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=80, default="Bogotá")
    nivel = models.CharField(max_length=20, choices=NIVELES, default="recreativo")
    descripcion = models.CharField(max_length=220, blank=True)
    foto = models.FileField(upload_to="equipos/", blank=True, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])])
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name="equipos_creados")
    miembros = models.ManyToManyField(User, related_name="equipos", blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre


class SolicitudEquipo(models.Model):
    ESTADOS = [("pendiente", "Pendiente"), ("aceptada", "Aceptada"), ("rechazada", "Rechazada")]
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="solicitudes")
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name="solicitudes_equipo")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("equipo", "solicitante"), name="unique_team_request")]
        ordering = ("-creada_en",)
