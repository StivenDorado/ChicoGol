from django.urls import path

from .views import crear_partido, detalle_partido, gestionar_inscripcion, lista_partidos

app_name = "partidos"
urlpatterns = [
    path("", lista_partidos, name="lista"),
    path("crear/", crear_partido, name="crear"),
    path("<int:pk>/inscripciones/<int:inscripcion_id>/<str:accion>/", gestionar_inscripcion, name="gestionar_inscripcion"),
    path("<int:pk>/", detalle_partido, name="detalle"),
]
