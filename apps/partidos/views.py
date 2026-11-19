from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.notificaciones.models import Notificacion
from apps.social.models import ChatGrupo
from apps.canchas.models import Cancha
from config.transactions import atomic

from .forms import PartidoFiltroForm, PartidoForm
from .models import InscripcionPartido, Partido


@login_required
def lista_partidos(request):
    form = PartidoFiltroForm(request.GET or None)
    partidos = Partido.objects.filter(fecha__gte=timezone.now()).select_related("equipo", "cancha")
    if form.is_valid():
        ciudad = form.cleaned_data.get("ciudad", "").strip()
        barrio = form.cleaned_data.get("barrio", "").strip()
        fecha = form.cleaned_data.get("fecha")
        nivel = form.cleaned_data.get("nivel", "")
        if ciudad:
            partidos = partidos.filter(Q(cancha__ciudad__icontains=ciudad) | Q(cancha__barrio__icontains=ciudad))
        if barrio:
            partidos = partidos.filter(cancha__barrio__icontains=barrio)
        if fecha:
            partidos = partidos.filter(fecha__date=fecha)
        if nivel:
            partidos = partidos.filter(nivel=nivel)
    return render(request, "partidos/lista.html", {"partidos": partidos, "filtro_form": form})


@login_required
def detalle_partido(request, pk):
    partido = get_object_or_404(Partido.objects.select_related("equipo", "cancha"), pk=pk)
    if request.method == "POST":
        with atomic():
            partido = Partido.objects.select_for_update().get(pk=partido.pk)
            inscripcion = partido.inscripciones.filter(jugador=request.user).first()
            if inscripcion is None and partido.cupos_disponibles > 0:
                titulares = partido.inscripciones.filter(estado="aceptada", rol="titular").count()
                inscripcion = InscripcionPartido.objects.create(partido=partido, jugador=request.user, estado="aceptada", rol="titular" if titulares < 10 else "recambio")
                partido.jugadores.add(request.user)
                chat = partido.chats.first()
                if chat is None:
                    chat = ChatGrupo.objects.create(nombre=f"Chat · {partido.equipo.nombre} · {partido.cancha.nombre}", equipo=partido.equipo, partido=partido)
                    chat.miembros.add(partido.creador)
                chat.miembros.add(request.user)
                Notificacion.objects.create(usuario=partido.creador, tipo="partido", titulo="Nuevo jugador en tu partido", mensaje=f"{request.user.get_full_name() or request.user.username} se unió a tu partido.", url=reverse("partidos:detalle", args=[partido.pk]))
            elif inscripcion and inscripcion.estado != "aceptada" and partido.cupos_disponibles > 0:
                titulares = partido.inscripciones.filter(estado="aceptada", rol="titular").count()
                inscripcion.estado = "aceptada"
                inscripcion.rol = "titular" if titulares < 10 else "recambio"
                inscripcion.save(update_fields=["estado", "rol"])
                partido.jugadores.add(request.user)
                chat = partido.chats.first()
                if chat:
                    chat.miembros.add(request.user)
        return redirect("partidos:detalle", pk=pk)
    inscripcion_usuario = partido.inscripciones.filter(jugador=request.user).first()
    return render(request, "partidos/detalle.html", {"partido": partido, "inscripcion_usuario": inscripcion_usuario, "ya_inscrito": bool(inscripcion_usuario and inscripcion_usuario.estado == "aceptada"), "inscripciones": partido.inscripciones.filter(estado="aceptada").select_related("jugador__perfil"), "solicitudes": partido.inscripciones.filter(estado="pendiente").select_related("jugador__perfil") if request.user == partido.creador else [], "es_creador": request.user == partido.creador})


@login_required
def crear_partido(request):
    form = PartidoForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        with atomic():
            partido = form.save(commit=False)
            partido.creador = request.user
            partido.cupos = 11
            partido.save()
            partido.jugadores.add(request.user)
            InscripcionPartido.objects.create(partido=partido, jugador=request.user, rol="titular", estado="aceptada")
            chat = ChatGrupo.objects.create(nombre=f"Chat · {partido.equipo.nombre} · {partido.cancha.nombre}", equipo=partido.equipo, partido=partido)
            chat.miembros.add(request.user)
            Notificacion.objects.create(usuario=request.user, tipo="partido", titulo="Partido publicado", mensaje="Tu partido quedó disponible para recibir jugadores.", url=reverse("partidos:detalle", args=[partido.pk]))
        return redirect("partidos:detalle", pk=partido.pk)
    return render(request, "partidos/form.html", {"form": form, "canchas_disponibles": Cancha.objects.filter(activa=True).order_by("ciudad", "nombre")})


@login_required
def gestionar_inscripcion(request, pk, inscripcion_id, accion):
    partido = get_object_or_404(Partido, pk=pk)
    if request.user != partido.creador:
        raise PermissionDenied
    inscripcion = get_object_or_404(InscripcionPartido, pk=inscripcion_id, partido=partido)
    if request.method != "POST" or inscripcion.estado != "pendiente":
        return redirect("partidos:detalle", pk=partido.pk)
    with atomic():
        partido = Partido.objects.select_for_update().get(pk=partido.pk)
        inscripcion = InscripcionPartido.objects.select_for_update().get(pk=inscripcion.pk)
        if accion == "aceptar":
            if partido.cupos_disponibles <= 0:
                return redirect("partidos:detalle", pk=partido.pk)
            inscripcion.estado = "aceptada"
            inscripcion.rol = "recambio" if partido.inscripciones.filter(estado="aceptada", rol="recambio").exists() else "titular"
            partido.jugadores.add(inscripcion.jugador)
            for chat in partido.chats.all():
                chat.miembros.add(inscripcion.jugador)
            mensaje = f"Tu solicitud para el partido de {partido.equipo.nombre} fue aceptada."
        elif accion == "rechazar":
            inscripcion.estado = "rechazada"
            mensaje = f"Tu solicitud para el partido de {partido.equipo.nombre} fue rechazada."
        else:
            raise PermissionDenied
        inscripcion.save(update_fields=["estado", "rol"])
        Notificacion.objects.create(usuario=inscripcion.jugador, tipo="partido", titulo="Solicitud de partido actualizada", mensaje=mensaje, url=reverse("partidos:detalle", args=[partido.pk]))
    return redirect("partidos:detalle", pk=partido.pk)
