from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CanchaFiltroForm, CanchaForm, ResenaCanchaForm
from .models import Cancha, ResenaCancha


def lista_canchas(request):
    form = CanchaFiltroForm(request.GET or None)
    canchas = Cancha.objects.filter(activa=True)
    if form.is_valid():
        query = form.cleaned_data.get("q", "").strip()
        modalidad = form.cleaned_data.get("modalidad", "")
        if query:
            canchas = canchas.filter(Q(nombre__icontains=query) | Q(barrio__icontains=query) | Q(ciudad__icontains=query))
        if modalidad:
            canchas = canchas.filter(modalidad=modalidad)
    canchas = list(canchas)
    mapa = [
        {"id": cancha.pk, "nombre": cancha.nombre, "direccion": cancha.direccion,
         "ciudad": cancha.ciudad, "latitud": float(cancha.latitud), "longitud": float(cancha.longitud)}
        for cancha in canchas if cancha.latitud is not None and cancha.longitud is not None
    ]
    return render(request, "canchas/lista.html", {"form": form, "canchas": canchas, "total": len(canchas), "canchas_mapa": mapa})


@login_required
def crear_cancha(request):
    form = CanchaForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        cancha = form.save(commit=False)
        cancha.activa = True
        cancha.save()
        return redirect("canchas:detalle", pk=cancha.pk)
    return render(request, "canchas/lista.html", {"create_form": form})


def detalle_cancha(request, pk):
    cancha = get_object_or_404(Cancha, pk=pk, activa=True)
    resenas = cancha.resenas.select_related("usuario").all()
    mi_resena = resenas.filter(usuario=request.user).first() if request.user.is_authenticated else None
    return render(request, "canchas/detalle.html", {
        "cancha": cancha,
        "resenas": resenas,
        "promedio_resenas": sum(resena.calificacion for resena in resenas) / resenas.count() if resenas.exists() else 0,
        "total_resenas": resenas.count(),
        "mi_resena": mi_resena,
        "resena_form": ResenaCanchaForm(instance=mi_resena),
    })


@login_required
def guardar_resena(request, pk):
    cancha = get_object_or_404(Cancha, pk=pk, activa=True)
    resena = ResenaCancha.objects.filter(cancha=cancha, usuario=request.user).first()
    if request.method == "POST":
        form = ResenaCanchaForm(request.POST, instance=resena)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.cancha = cancha
            resena.usuario = request.user
            resena.save()
    return redirect("canchas:detalle", pk=cancha.pk)
