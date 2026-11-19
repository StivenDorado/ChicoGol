from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Cancha(models.Model):
    TIPO_CHOICES = [("sintetica", "Sintética"), ("natural", "Natural"), ("cemento", "Cemento")]
    MODALIDAD_CHOICES = [("f5", "Fútbol 5"), ("f8", "Fútbol 8"), ("f11", "Fútbol 11")]
    nombre = models.CharField(max_length=120)
    ciudad = models.CharField(max_length=80, default="Bogotá")
    barrio = models.CharField(max_length=80, blank=True)
    direccion = models.CharField(max_length=180)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="sintetica")
    modalidad = models.CharField(max_length=10, choices=MODALIDAD_CHOICES, default="f5")
    precio_hora = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    foto = models.FileField(upload_to="canchas/", blank=True, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])])
    servicios = models.CharField(max_length=220, blank=True, help_text="Separa los servicios con coma")
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("ciudad", "nombre")
        verbose_name = "Cancha"
        verbose_name_plural = "Canchas"

    def __str__(self):
        return f"{self.nombre} · {self.ciudad}"

    @property
    def servicios_lista(self):
        return [item.strip() for item in self.servicios.split(",") if item.strip()]


class ResenaCancha(models.Model):
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, related_name="resenas")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resenas_canchas")
    calificacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(max_length=600)
    creada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-creada_en",)
        constraints = [
            models.UniqueConstraint(fields=("cancha", "usuario"), name="unique_court_review_by_user"),
        ]

    def __str__(self):
        return f"{self.cancha.nombre} · {self.calificacion}/5 · {self.usuario.username}"
