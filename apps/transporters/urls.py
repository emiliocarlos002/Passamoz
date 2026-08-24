from django.urls import path
from .activation_views import TransporterActivationView
from .views import (
    ApplyTransporterView,
    PaymentAccountListView,
    RouteListView,
    TransporterDashboardView,
    VehicleListView,
)

urlpatterns = [
    path("ativar/<uidb64>/<token>/", TransporterActivationView.as_view(), name="transporter-activate"),
    path("candidatura/", ApplyTransporterView.as_view(), name="transporter-apply"),
    path("", TransporterDashboardView.as_view(), name="transporter-dashboard"),
    path("rotas/", RouteListView.as_view(), name="transporter-routes"),
    path("veiculos/", VehicleListView.as_view(), name="transporter-vehicles"),
    path(
        "pagamentos/",
        PaymentAccountListView.as_view(),
        name="transporter-payments",
    ),
]
