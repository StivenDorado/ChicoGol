from django.contrib import admin

from .models import Equipo


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ciudad", "nivel", "creador")
    list_filter = ("ciudad", "nivel")
    search_fields = ("nombre", "ciudad")
