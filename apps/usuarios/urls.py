from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import LoginView, mi_cancha, perfil, registro

app_name = "usuarios"
urlpatterns = [
    path("registro/", registro, name="registro"),
    path("iniciar-sesion/", LoginView.as_view(), name="login"),
    path("cerrar-sesion/", LogoutView.as_view(), name="logout"),
    path("mi-cancha/", mi_cancha, name="mi_cancha"),
    path("perfil/", perfil, name="perfil"),
]
