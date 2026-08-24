from django.urls import path
from .views import (
    SubscriptionListView,
    SubscriptionMarkPaidView,
    TransporterAdminListView,
    TransporterApproveView,
    TransporterRejectView,
    TransporterResendActivationView,
    TransporterSuspendView,
)

urlpatterns = [
    path(
        "operadoras/",
        TransporterAdminListView.as_view(),
        name="platform-transporters",
    ),
    path(
        "operadoras/<int:pk>/aprovar/",
        TransporterApproveView.as_view(),
        name="platform-transporter-approve",
    ),
    path(
        "operadoras/<int:pk>/reenviar-ativacao/",
        TransporterResendActivationView.as_view(),
        name="platform-transporter-resend-activation",
    ),
    path(
        "operadoras/<int:pk>/rejeitar/",
        TransporterRejectView.as_view(),
        name="platform-transporter-reject",
    ),
    path(
        "operadoras/<int:pk>/suspender/",
        TransporterSuspendView.as_view(),
        name="platform-transporter-suspend",
    ),
    path(
        "mensalidades/",
        SubscriptionListView.as_view(),
        name="platform-subscriptions",
    ),
    path(
        "mensalidades/<int:pk>/pagar/",
        SubscriptionMarkPaidView.as_view(),
        name="platform-subscription-paid",
    ),
]
