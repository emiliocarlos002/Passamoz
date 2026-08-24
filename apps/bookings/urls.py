from django.urls import path
from .views import BookingPaymentView, CreateBookingView, SearchTripsView

urlpatterns = [
    path("", SearchTripsView.as_view(), name="trip-search"),
    path(
        "trip/<int:trip_id>/reservar/",
        CreateBookingView.as_view(),
        name="booking-create",
    ),
    path(
        "<uuid:reference>/pagamento/",
        BookingPaymentView.as_view(),
        name="booking-payment",
    ),
]
