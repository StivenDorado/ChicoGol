from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from apps.notificaciones.models import Notificacion
from apps.social.models import ChatGrupo
from config.transactions import atomic

from .forms import EquipoForm
from .models import Equipo, SolicitudEquipo


def lista_equipos(request):
    equipos = Equipo.objects.all()
    return render(request, "equipos/lista.html", {"equipos": equipos})


def detalle_equipo(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("usuarios:login"))
        if not equipo.miembros.filter(pk=request.user.pk).exists():
            solicitud, _ = SolicitudEquipo.objects.get_or_create(equipo=equipo, solicitante=request.user, defaults={"estado": "pendiente"})
            if solicitud.estado != "aceptada":
                solicitud.estado = "pendiente"
                solicitud.save(update_fields=["estado", "actualizada_en"])
                Notificacion.objects.create(usuario=equipo.creador, tipo="equipo", titulo="Solicitud para unirse", mensaje=f"{request.user.get_full_name() or request.user.username} quiere unirse a {equipo.nombre}.", url=reverse("equipos:detalle", args=[equipo.pk]))
        return redirect("equipos:detalle", pk=pk)
    solicitud_usuario = SolicitudEquipo.objects.filter(equipo=equipo, solicitante=request.user).first() if request.user.is_authenticated else None
    solicitudes = equipo.solicitudes.filter(estado="pendiente").select_related("solicitante") if request.user == equipo.creador else []
    return render(request, "equipos/detalle.html", {"equipo": equipo, "es_miembro": request.user.is_authenticated and equipo.miembros.filter(pk=request.user.pk).exists(), "solicitud_usuario": solicitud_usuario, "solicitudes": solicitudes, "es_creador": request.user == equipo.creador})


@login_required
def crear_equipo(request):
    form = EquipoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        equipo = form.save(commit=False)
        equipo.creador = request.user
        equipo.save()
        equipo.miembros.add(request.user)
        chat = ChatGrupo.objects.create(nombre=f"Chat · {equipo.nombre}", equipo=equipo)
        chat.miembros.add(request.user)
        Notificacion.objects.create(usuario=request.user, tipo="equipo", titulo="Equipo creado", mensaje=f"{equipo.nombre} ya está listo para organizar partidos.", url=reverse("equipos:detalle", args=[equipo.pk]))
        return redirect("equipos:detalle", pk=equipo.pk)
    return render(request, "equipos/form.html", {"form": form})


@login_required
def gestionar_solicitud(request, pk, solicitud_id, accion):
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.user != equipo.creador:
        raise PermissionDenied
    solicitud = get_object_or_404(SolicitudEquipo, pk=solicitud_id, equipo=equipo)
    if request.method != "POST" or solicitud.estado != "pendiente":
        return redirect("equipos:detalle", pk=equipo.pk)
    with atomic():
        if accion == "aceptar":
            solicitud.estado = "aceptada"
            equipo.miembros.add(solicitud.solicitante)
            for chat in equipo.chats.all():
                chat.miembros.add(solicitud.solicitante)
            mensaje = f"Tu solicitud para unirte a {equipo.nombre} fue aceptada."
        elif accion == "rechazar":
            solicitud.estado = "rechazada"
            mensaje = f"Tu solicitud para unirte a {equipo.nombre} fue rechazada."
        else:
            raise PermissionDenied
        solicitud.save(update_fields=["estado", "actualizada_en"])
        Notificacion.objects.create(usuario=solicitud.solicitante, tipo="equipo", titulo="Solicitud de equipo actualizada", mensaje=mensaje, url=reverse("equipos:detalle", args=[equipo.pk]))
    return redirect("equipos:detalle", pk=equipo.pk)
