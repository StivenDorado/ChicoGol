from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Perfil(models.Model):
    POSICIONES = [("portero", "Portero"), ("defensa", "Defensa"), ("medio", "Mediocampista"), ("delantero", "Delantero"), ("polivalente", "Polivalente")]
    NIVELES = [("recreativo", "Recreativo"), ("intermedio", "Intermedio"), ("competitivo", "Competitivo")]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    ciudad = models.CharField(max_length=80, blank=True)
    barrio = models.CharField(max_length=80, blank=True)
    posicion = models.CharField(max_length=20, choices=POSICIONES, default="polivalente")
    nivel = models.CharField(max_length=20, choices=NIVELES, default="recreativo")
    bio = models.CharField(max_length=220, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    edad = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(13), MaxValueValidator(100)])
    telefono = models.CharField(max_length=30, blank=True)
    avatar = models.FileField(upload_to="avatars/", blank=True, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])])
    actualizado_en = models.DateTimeField(auto_now=True)

    @property
    def es_menor(self):
        return self.edad is not None and self.edad < 18

    def calcular_edad(self):
        if not self.fecha_nacimiento:
            return self.edad
        hoy = timezone.localdate()
        return hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

    def __str__(self):
        return f"Perfil de {self.usuario.username}"
