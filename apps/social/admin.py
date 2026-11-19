from django.contrib import admin

from .models import ChatGrupo, Mensaje, SolicitudAmistad

admin.site.register((SolicitudAmistad, ChatGrupo, Mensaje))
