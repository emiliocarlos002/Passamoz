from django import forms
from .models import Trip

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
            "departure_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "arrival_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
