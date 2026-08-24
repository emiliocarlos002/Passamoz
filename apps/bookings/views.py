from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from apps.trips.models import Trip, TripSeat
from .models import Booking


class SearchTripsView(View):
    def get(self, request):
        # Keep the legacy /compras/ URL working while using the main passenger flow.
        return redirect("passengerpanel:search")


class CreateBookingView(LoginRequiredMixin, View):
    login_url = "/conta/entrar/"

    @transaction.atomic
    def post(self, request, trip_id):
        trip = get_object_or_404(
            Trip.objects.select_related("transporter"),
            pk=trip_id,
            status=Trip.Status.PUBLISHED,
        )
        trip_seat = get_object_or_404(
            TripSeat.objects.select_for_update().select_related("seat"),
            pk=request.POST.get("trip_seat_id"),
            trip=trip,
            is_available=True,
        )
        booking = Booking.objects.create(
            passenger=request.user,
            trip=trip,
            trip_seat=trip_seat,
            amount=trip.price,
            status=Booking.Status.PENDING,
        )
        trip_seat.is_available = False
        trip_seat.save(update_fields=["is_available"])
        return redirect("passengerpanel:payment", reference=booking.reference)


class BookingPaymentView(LoginRequiredMixin, View):
    login_url = "/conta/entrar/"

    def get(self, request, reference):
        return redirect("passengerpanel:payment", reference=reference)

    def post(self, request, reference):
        return redirect("passengerpanel:payment", reference=reference)
