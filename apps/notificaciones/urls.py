from django.urls import path

from .views import lista_notificaciones

app_name = "notificaciones"
urlpatterns = [path("", lista_notificaciones, name="lista")]
