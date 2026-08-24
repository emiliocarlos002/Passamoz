import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q
from apps.trips.models import Trip, TripSeat


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        PAYMENT_PROCESSING = "payment_processing", "Pagamento em processamento"
        PAID = "paid", "Pago"
        EXPIRED = "expired", "Expirado"
        CANCELLED = "cancelled", "Cancelado"
        REFUNDED = "refunded", "Reembolsado"

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings")
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, related_name="bookings")
    trip_seat = models.ForeignKey(TripSeat, on_delete=models.PROTECT, related_name="bookings")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip_seat"],
                condition=Q(status__in=["pending", "payment_processing", "paid"]),
                name="unique_active_booking_per_trip_seat",
            )
        ]
        indexes = [
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["passenger", "created_at"]),
        ]


class BookingPassenger(models.Model):
    """Passenger/item within a booking, allowing one checkout to cover several seats."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="passengers")
    trip_seat = models.ForeignKey(TripSeat, on_delete=models.PROTECT, related_name="booking_passengers")
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    passenger_type = models.CharField(max_length=30, default="adult")
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["booking", "trip_seat"], name="unique_booking_passenger_seat"),
        ]


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="payments")
    provider = models.CharField(max_length=20)
    transaction_reference = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30, default="submitted")
    gateway_reference = models.CharField(max_length=150, blank=True)
    gateway_status = models.CharField(max_length=50, blank=True)
    payer_phone = models.CharField(max_length=30, blank=True)
    idempotency_key = models.CharField(max_length=150, blank=True, unique=True, null=True)
    webhook_event_id = models.CharField(max_length=150, blank=True, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "transaction_reference"],
                name="unique_payment_transaction_reference",
            )
        ]
        indexes = [
            models.Index(fields=["gateway_reference"]),
            models.Index(fields=["status", "created_at"]),
        ]
