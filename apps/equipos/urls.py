from django.urls import path

from .views import crear_equipo, detalle_equipo, gestionar_solicitud, lista_equipos

app_name = "equipos"
urlpatterns = [
    path("", lista_equipos, name="lista"),
    path("crear/", crear_equipo, name="crear"),
    path("<int:pk>/solicitudes/<int:solicitud_id>/<str:accion>/", gestionar_solicitud, name="gestionar_solicitud"),
    path("<int:pk>/", detalle_equipo, name="detalle"),
]
