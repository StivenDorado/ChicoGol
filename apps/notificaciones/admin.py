from django.contrib import admin

from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "titulo", "tipo", "leida", "creada_en")
    list_filter = ("tipo", "leida")
