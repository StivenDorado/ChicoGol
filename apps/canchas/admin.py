from django.contrib import admin

from .models import Cancha


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ciudad", "barrio", "modalidad", "tipo", "precio_hora", "activa")
    list_filter = ("ciudad", "modalidad", "tipo", "activa")
    search_fields = ("nombre", "barrio", "direccion")
