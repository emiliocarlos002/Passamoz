from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms import TripForm
from .models import Trip
from .services import initialize_trip_seats

class TransporterTripMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.transporter = request.user.transporter_profile
        except Exception as exc:
            raise PermissionDenied("Conta sem operadora.") from exc
        if self.transporter.status != "active":
            raise PermissionDenied("Operadora não está ativa.")
        return super().dispatch(request, *args, **kwargs)

class TripListView(TransporterTripMixin, View):
    def get(self, request):
        trips = self.transporter.trips.select_related("route", "vehicle")
        return render(request, "trips/list.html", {"trips": trips})

class TripCreateView(TransporterTripMixin, View):
    def get_form(self, data=None):
        form = TripForm(data)
        form.fields["route"].queryset = self.transporter.routes.filter(active=True)
        form.fields["vehicle"].queryset = self.transporter.vehicles.filter(active=True)
        return form

    def get(self, request):
        return render(
            request,
            "trips/form.html",
            {"form": self.get_form()},
        )

    def post(self, request):
        form = self.get_form(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.transporter = self.transporter
            trip.save()
            initialize_trip_seats(trip)
            messages.success(request, "Viagem criada.")
            return redirect("trip-list")
        return render(
            request,
            "trips/form.html",
            {"form": form},
        )

class PublishTripView(TransporterTripMixin, View):
    def post(self, request, pk):
        trip = get_object_or_404(
            Trip,
            pk=pk,
            transporter=self.transporter,
        )
        trip.status = Trip.Status.PUBLISHED
        trip.save(update_fields=["status"])
        return redirect("trip-list")
