from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.notificaciones.models import Notificacion
from apps.usuarios.models import Perfil

from .forms import MensajeForm
from .models import ChatGrupo, Mensaje, SolicitudAmistad


def jugadores(request):
    query = request.GET.get("q", "").strip()
    personas = User.objects.filter(is_active=True).exclude(pk=request.user.pk if request.user.is_authenticated else None).select_related("perfil")
    if query:
        personas = personas.filter(username__icontains=query) | personas.filter(first_name__icontains=query) | personas.filter(last_name__icontains=query)
    return render(request, "social/jugadores.html", {"personas": personas.distinct(), "query": query})


def perfil_publico(request, pk):
    persona = get_object_or_404(User.objects.select_related("perfil"), pk=pk, is_active=True)
    Perfil.objects.get_or_create(usuario=persona)
    return render(request, "social/perfil_publico.html", {"persona": persona})


@login_required
def amigos(request):
    recibidas = request.user.solicitudes_recibidas.filter(estado="pendiente").select_related("emisor")
    aceptadas = SolicitudAmistad.objects.filter(estado="aceptada").filter(emisor=request.user) | SolicitudAmistad.objects.filter(estado="aceptada").filter(receptor=request.user)
    return render(request, "social/amigos.html", {"recibidas": recibidas, "amistades": aceptadas.select_related("emisor", "receptor")})


@login_required
def enviar_solicitud(request, pk):
    receptor = get_object_or_404(User, pk=pk, is_active=True)
    if receptor != request.user and request.method == "POST":
        SolicitudAmistad.objects.get_or_create(emisor=request.user, receptor=receptor)
        Notificacion.objects.create(usuario=receptor, tipo="social", titulo="Nueva solicitud de amistad", mensaje=f"{request.user.get_full_name() or request.user.username} quiere conectar contigo.", url=reverse("social:amigos"))
    return redirect("social:jugadores")


@login_required
def aceptar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudAmistad, pk=pk, receptor=request.user)
    if request.method == "POST":
        solicitud.estado = "aceptada"
        solicitud.save(update_fields=["estado"])
        Notificacion.objects.create(usuario=solicitud.emisor, tipo="social", titulo="Solicitud aceptada", mensaje=f"{request.user.get_full_name() or request.user.username} aceptó tu solicitud.", url=reverse("social:amigos"))
    return redirect("social:amigos")


@login_required
def chats(request):
    return render(request, "social/chats.html", {"chats": request.user.chats.all()})


@login_required
def chat_detalle(request, pk):
    chat = get_object_or_404(request.user.chats, pk=pk)
    form = MensajeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        mensaje = form.save(commit=False)
        mensaje.chat = chat
        mensaje.autor = request.user
        mensaje.save()
        return redirect("social:chat", pk=pk)
    return render(request, "social/chat.html", {"chat": chat, "form": form, "mensajes": chat.mensajes.select_related("autor")})
