from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.tickets.models import Ticket
from .models import Booking, BookingPassenger, Payment

HOLD_MINUTES = 15
ACTIVE_STATUSES = {Booking.Status.PENDING, Booking.Status.PAYMENT_PROCESSING, Booking.Status.PAID}


def booking_expiry():
    return timezone.now() + timedelta(minutes=HOLD_MINUTES)


@transaction.atomic
def expire_booking(booking):
    booking = Booking.objects.select_for_update().select_related("trip_seat").get(pk=booking.pk)
    if booking.status not in {Booking.Status.PENDING, Booking.Status.PAYMENT_PROCESSING}:
        return False
    if booking.expires_at and booking.expires_at > timezone.now():
        return False
    booking.status = Booking.Status.EXPIRED
    booking.cancelled_at = timezone.now()
    booking.save(update_fields=["status", "cancelled_at"])
    # A TripSeat may have a different active booking only if data was manually repaired.
    seat = booking.trip_seat
    if not Booking.objects.filter(trip_seat=seat, status__in=ACTIVE_STATUSES).exclude(pk=booking.pk).exists():
        seat.is_available = True
        seat.save(update_fields=["is_available"])
    return True


@transaction.atomic
def confirm_payment(payment_id):
    payment = Payment.objects.select_for_update().select_related("booking__trip_seat").get(pk=payment_id)
    booking = Booking.objects.select_for_update().get(pk=payment.booking_id)
    if payment.amount != booking.amount:
        payment.status = "rejected"
        payment.gateway_status = "amount_mismatch"
        payment.save(update_fields=["status", "gateway_status", "updated_at"])
        return booking, None
    if booking.status == Booking.Status.PAID:
        payment.status = "confirmed"
        payment.confirmed_at = payment.confirmed_at or timezone.now()
        payment.save(update_fields=["status", "confirmed_at", "updated_at"])
        return booking, Ticket.objects.get_or_create(booking=booking)[0]
    if booking.status in {Booking.Status.CANCELLED, Booking.Status.EXPIRED, Booking.Status.REFUNDED}:
        payment.status = "rejected"
        payment.gateway_status = "booking_not_payable"
        payment.save(update_fields=["status", "gateway_status", "updated_at"])
        return booking, None
    booking.status = Booking.Status.PAID
    booking.paid_at = timezone.now()
    booking.expires_at = None
    booking.save(update_fields=["status", "paid_at", "expires_at"])
    payment.status = "confirmed"
    payment.confirmed_at = timezone.now()
    payment.save(update_fields=["status", "confirmed_at", "updated_at"])
    ticket, _ = Ticket.objects.get_or_create(booking=booking)
    return booking, ticket


def create_booking_passengers(booking, passenger_data):
    """Create passenger records; the booking's original seat remains the primary seat."""
    created = []
    for item in passenger_data:
        created.append(BookingPassenger.objects.create(booking=booking, **item))
    return created


@transaction.atomic
def create_multi_seat_booking(*, user, trip, trip_seat_ids, passenger_data):
    """Reserve several seats in one checkout, atomically.

    trip_seat_ids and passenger_data must have the same length. The first seat is
    kept as Booking.trip_seat for backwards compatibility; all seats are stored
    in BookingPassenger rows.
    """
    if not trip_seat_ids or len(trip_seat_ids) != len(passenger_data):
        raise ValueError("É necessário fornecer um passageiro para cada lugar.")
    from apps.trips.models import TripSeat
    seats = list(
        TripSeat.objects.select_for_update().select_related("seat")
        .filter(trip=trip, id__in=trip_seat_ids)
        .order_by("id")
    )
    if len(seats) != len(set(trip_seat_ids)) or any(not seat.is_available for seat in seats):
        raise ValueError("Um ou mais lugares já não estão disponíveis.")
    if Booking.objects.filter(trip_seat__in=seats, status__in=ACTIVE_STATUSES).exists():
        raise ValueError("Um ou mais lugares já possuem uma reserva ativa.")
    total = Decimal(trip.price) * len(seats)
    booking = Booking.objects.create(
        passenger=user, trip=trip, trip_seat=seats[0], amount=total,
        status=Booking.Status.PENDING, expires_at=booking_expiry(),
    )
    for seat, data in zip(seats, passenger_data):
        BookingPassenger.objects.create(
            booking=booking, trip_seat=seat, **data
        )
        seat.is_available = False
        seat.save(update_fields=["is_available"])
    return booking
