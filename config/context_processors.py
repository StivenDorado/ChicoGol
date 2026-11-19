def app_context(request):
    if not request.user.is_authenticated:
        return {"unread_notifications": 0, "current_profile": None}
    from apps.usuarios.models import Perfil

    profile, _ = Perfil.objects.get_or_create(usuario=request.user)
    return {
        "unread_notifications": request.user.notificaciones.filter(leida=False).count(),
        "current_profile": profile,
    }
