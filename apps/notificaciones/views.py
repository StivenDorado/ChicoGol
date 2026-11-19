from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Notificacion


@login_required
def lista_notificaciones(request):
    notificaciones = request.user.notificaciones.all()
    if request.method == "POST":
        notificaciones.filter(leida=False).update(leida=True)
        return redirect("notificaciones:lista")
    return render(request, "notificaciones/lista.html", {"notificaciones": notificaciones})
