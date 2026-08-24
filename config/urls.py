from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("notificacoes/", include("apps.notifications.urls")),
    path("validar-bilhete/", include("apps.qrvalidation.urls")),
    path("passageiro/", include("apps.passengerpanel.urls")),
    path("painel-operadora/", include("apps.operatorpanel.urls")),
    path("painel-admin/", include("apps.adminpanel.urls")),
    path("django-admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("operadora/", include("apps.transporters.urls")),
    path("viagens/", include("apps.trips.urls")),
    path("compras/", include("apps.bookings.urls")),
    path("bilhetes/", include("apps.tickets.urls")),
    path("plataforma/", include("apps.platform.urls")),
    path("api/v1/", include("apps.api.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
