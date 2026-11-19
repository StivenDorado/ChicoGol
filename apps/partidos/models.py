from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from apps.canchas.models import Cancha
from apps.equipos.models import Equipo


class Partido(models.Model):
    NIVELES = Equipo.NIVELES
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="partidos")
    cancha = models.ForeignKey(Cancha, on_delete=models.PROTECT, related_name="partidos")
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name="partidos_creados")
    fecha = models.DateTimeField(default=timezone.now)
    cupos = models.PositiveSmallIntegerField(default=11)
    nivel = models.CharField(max_length=20, choices=NIVELES, default="recreativo")
    descripcion = models.CharField(max_length=220, blank=True)
    jugadores = models.ManyToManyField(User, related_name="partidos", blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("fecha",)

    def __str__(self):
        return f"{self.equipo} · {self.fecha:%d/%m %H:%M}"

    @property
    def cupos_disponibles(self):
        aceptados = set(self.inscripciones.filter(estado="aceptada").values_list("jugador_id", flat=True))
        legacy_players = self.jugadores.exclude(pk__in=aceptados).count() if aceptados else self.jugadores.count()
        ocupados = len(aceptados) + legacy_players
        return max(0, 11 - ocupados)


class InscripcionPartido(models.Model):
    ESTADOS = [("pendiente", "Pendiente"), ("aceptada", "Aceptada"), ("rechazada", "Rechazada")]
    ROLES = [("titular", "Titular"), ("recambio", "Recambio")]
    POSICIONES = [("portero", "Portero"), ("defensa", "Defensa"), ("medio", "Mediocampo"), ("delantero", "Delantero")]
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name="inscripciones")
    jugador = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inscripciones_partido")
    rol = models.CharField(max_length=20, choices=ROLES, default="titular")
    posicion = models.CharField(max_length=20, choices=POSICIONES, default="medio")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("partido", "jugador"), name="unique_match_player")]
