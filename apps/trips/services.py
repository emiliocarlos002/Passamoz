from django.db import transaction
from .models import TripSeat

@transaction.atomic
def initialize_trip_seats(trip):
    TripSeat.objects.bulk_create(
        [
            TripSeat(trip=trip, seat=seat)
            for seat in trip.vehicle.seats.filter(active=True)
        ],
        ignore_conflicts=True,
    )
