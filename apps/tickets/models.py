import uuid
from django.db import models
from apps.bookings.models import Booking

class Ticket(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.PROTECT,
        related_name="ticket",
    )
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to="tickets/", blank=True)
