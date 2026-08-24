from django.urls import path
from .payment_webhook import payment_webhook
from .views import HealthView, PublishedTripsView


urlpatterns = [
    path("health/", HealthView.as_view(), name="api-health"),
    path("trips/", PublishedTripsView.as_view(), name="api-trips"),
]

urlpatterns += [path("payments/webhook/", payment_webhook, name="payment-webhook")]
