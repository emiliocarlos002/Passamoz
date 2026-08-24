from django.db import models
from apps.transporters.models import Route, Seat, Transporter, Vehicle

class Trip(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        PUBLISHED = "published", "Publicada"
        CANCELLED = "cancelled", "Cancelada"
        FINISHED = "finished", "Finalizada"

    transporter = models.ForeignKey(
        Transporter,
        on_delete=models.PROTECT,
        related_name="trips",
    )
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name="trips")
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="trips",
    )
    departure_at = models.DateTimeField()
    arrival_at = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="MZN")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

class TripSeat(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="trip_seats")
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT)
    is_available = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "seat"],
                name="unique_trip_seat",
            )
        ]
