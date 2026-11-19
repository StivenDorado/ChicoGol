from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.partidos.models import Partido
from .forms import DatosPersonalesForm, InicioSesionForm, PerfilForm, RegistroForm, calcular_edad
from .models import Perfil


class LoginView(auth_views.LoginView):
    template_name = "usuarios/login.html"
    authentication_form = InicioSesionForm
    redirect_authenticated_user = True


def inicio(request):
    if not request.user.is_authenticated:
        return render(request, "inicio.html")

    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    partidos = Partido.objects.filter(fecha__gte=timezone.now()).select_related("equipo", "cancha")[:3]
    equipos = request.user.equipos.all()[:3]
    return render(request, "inicio_autenticado.html", {"perfil": perfil, "partidos": partidos, "equipos": equipos})


def registro(request):
    if request.user.is_authenticated:
        return redirect("inicio")
    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Perfil.objects.update_or_create(
            usuario=user,
            defaults={
                "fecha_nacimiento": form.cleaned_data["fecha_nacimiento"],
                "edad": calcular_edad(form.cleaned_data["fecha_nacimiento"]),
            },
        )
        login(request, user)
        return redirect("inicio")
    return render(request, "usuarios/registro.html", {"form": form})


@login_required
def mi_cancha(request):
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    form = PerfilForm(request.POST or None, instance=perfil)
    datos_form = DatosPersonalesForm(request.POST or None, instance=request.user, prefix="datos")
    if request.method == "POST" and form.is_valid() and datos_form.is_valid():
        form.save()
        datos_form.save()
        return render(request, "usuarios/mi_cancha.html", {"form": form, "datos_form": datos_form, "guardado": True})
    return render(request, "usuarios/mi_cancha.html", {"form": form, "datos_form": datos_form})


@login_required
def perfil(request):
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    return render(request, "usuarios/perfil.html", {"perfil": perfil})
