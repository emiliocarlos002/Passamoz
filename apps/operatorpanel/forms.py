from django import forms

from apps.transporters.models import PaymentAccount, Route, Vehicle
from apps.trips.models import Trip


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ("origin", "destination", "active")


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ("name", "registration_plate", "capacity", "active")


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = (
            "route",
            "vehicle",
            "departure_at",
            "arrival_at",
            "price",
            "currency",
            "status",
        )
        widgets = {
            "departure_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "arrival_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, transporter=None, **kwargs):
        super().__init__(*args, **kwargs)
        if transporter is not None:
            self.fields["route"].queryset = transporter.routes.filter(active=True)
            self.fields["vehicle"].queryset = transporter.vehicles.filter(active=True)
        self.fields["departure_at"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["arrival_at"].input_formats = ("%Y-%m-%dT%H:%M",)


class PaymentAccountForm(forms.ModelForm):
    class Meta:
        model = PaymentAccount
        fields = ("provider", "account_name", "account_number", "is_active", "integration_mode", "payment_instructions", "gateway_wallet_id")
