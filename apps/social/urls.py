from django.urls import path

from .views import aceptar_solicitud, amigos, chat_detalle, chats, enviar_solicitud, jugadores, perfil_publico

app_name = "social"
urlpatterns = [
    path("jugadores/", jugadores, name="jugadores"),
    path("jugadores/<int:pk>/", perfil_publico, name="perfil_publico"),
    path("amigos/", amigos, name="amigos"),
    path("solicitud/<int:pk>/aceptar/", aceptar_solicitud, name="aceptar_solicitud"),
    path("solicitud/<int:pk>/enviar/", enviar_solicitud, name="enviar_solicitud"),
    path("chats/", chats, name="chats"),
    path("chats/<int:pk>/", chat_detalle, name="chat"),
]
