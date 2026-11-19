from django.urls import path

from .views import crear_cancha, detalle_cancha, guardar_resena, lista_canchas

app_name = "canchas"
urlpatterns = [
    path("", lista_canchas, name="lista"),
    path("crear/", crear_cancha, name="crear"),
    path("<int:pk>/resena/", guardar_resena, name="guardar_resena"),
    path("<int:pk>/", detalle_cancha, name="detalle"),
]
