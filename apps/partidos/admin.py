from django.contrib import admin

from .models import Partido


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ("equipo", "cancha", "fecha", "nivel", "cupos")
    list_filter = ("nivel", "cancha__ciudad")
    date_hierarchy = "fecha"
