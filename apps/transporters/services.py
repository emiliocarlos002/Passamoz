from django.db import transaction
from .models import Seat

@transaction.atomic
def generate_vehicle_seats(vehicle):
    if vehicle.seats.exists():
        return
    Seat.objects.bulk_create(
        [
            Seat(vehicle=vehicle, seat_number=str(number))
            for number in range(1, vehicle.capacity + 1)
        ]
    )
