from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.bookings.models import Booking
from apps.bookings.services import expire_booking


class Command(BaseCommand):
    help = "Expira reservas pendentes/processando cujo prazo terminou e liberta os lugares."

    def handle(self, *args, **options):
        qs = Booking.objects.filter(
            status__in=[Booking.Status.PENDING, Booking.Status.PAYMENT_PROCESSING],
            expires_at__isnull=False,
            expires_at__lte=timezone.now(),
        ).values_list("pk", flat=True)
        expired = 0
        for pk in qs.iterator():
            if expire_booking(Booking(pk=pk)):
                expired += 1
        self.stdout.write(self.style.SUCCESS(f"{expired} reserva(s) expirada(s)."))
