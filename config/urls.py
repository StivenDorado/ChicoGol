from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from apps.usuarios.views import inicio

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", inicio, name="inicio"),
    path("cuenta/", include("apps.usuarios.urls")),
    path("canchas/", include("apps.canchas.urls")),
    path("equipos/", include("apps.equipos.urls")),
    path("partidos/", include("apps.partidos.urls")),
    path("notificaciones/", include("apps.notificaciones.urls")),
    path("social/", include("apps.social.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
