from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.transporters.models import PaymentAccount, Route, Seat, Transporter, Vehicle
from apps.trips.models import Trip, TripSeat


class Command(BaseCommand):
    help = "Cria dados de demonstração do PassaMoz para testar pesquisa e reservas locais."

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username="operadora.demo@passamoz.local",
            defaults={
                "email": "operadora.demo@passamoz.local",
                "first_name": "Operadora",
                "last_name": "Demo",
            },
        )
        user.email = "operadora.demo@passamoz.local"
        user.set_password("PassaMoz123!")
        user.save()

        transporter, _ = Transporter.objects.get_or_create(
            owner=user,
            defaults={
                "name": "PassaMoz Demo",
                "legal_name": "PassaMoz Demo, Lda.",
                "phone": "+258 840000000",
                "email": "operadora.demo@passamoz.local",
                "status": Transporter.Status.ACTIVE,
            },
        )
        transporter.status = Transporter.Status.ACTIVE
        transporter.name = "PassaMoz Demo"
        transporter.save(update_fields=["status", "name"])

        route, _ = Route.objects.get_or_create(
            transporter=transporter,
            origin="Maputo",
            destination="Xai-Xai",
            defaults={"active": True},
        )
        route.active = True
        route.save(update_fields=["active"])

        vehicle, _ = Vehicle.objects.get_or_create(
            transporter=transporter,
            registration_plate="DEMO-01",
            defaults={"name": "Autocarro Demo", "capacity": 20, "active": True},
        )
        vehicle.name = "Autocarro Demo"
        vehicle.capacity = 20
        vehicle.active = True
        vehicle.save(update_fields=["name", "capacity", "active"])

        for number in range(1, 21):
            Seat.objects.get_or_create(
                vehicle=vehicle,
                seat_number=str(number),
                defaults={"active": True},
            )

        departure = timezone.now() + timedelta(days=2)
        trip, created = Trip.objects.get_or_create(
            transporter=transporter,
            route=route,
            vehicle=vehicle,
            departure_at=departure,
            defaults={
                "arrival_at": departure + timedelta(hours=4),
                "price": Decimal("850.00"),
                "currency": "MZN",
                "status": Trip.Status.PUBLISHED,
            },
        )
        if not created:
            trip.status = Trip.Status.PUBLISHED
            trip.price = Decimal("850.00")
            trip.currency = "MZN"
            trip.save(update_fields=["status", "price", "currency"])

        for seat in vehicle.seats.filter(active=True):
            TripSeat.objects.get_or_create(trip=trip, seat=seat)

        PaymentAccount.objects.get_or_create(
            transporter=transporter,
            provider=PaymentAccount.Provider.MPESA,
            defaults={
                "account_name": "PassaMoz Demo",
                "account_number": "840000000",
                "is_active": True,
            },
        )
        PaymentAccount.objects.get_or_create(
            transporter=transporter,
            provider=PaymentAccount.Provider.EMOLA,
            defaults={
                "account_name": "PassaMoz Demo",
                "account_number": "850000000",
                "is_active": True,
            },
        )
        PaymentAccount.objects.get_or_create(
            transporter=transporter,
            provider=PaymentAccount.Provider.BANK,
            defaults={
                "account_name": "Banco Demo (TESTE)",
                "account_number": "0000000000",
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Dados de demonstração criados com sucesso."))
        self.stdout.write("Pesquisa: Maputo -> Xai-Xai")
        self.stdout.write("Operadora demo: operadora.demo@passamoz.local")
        self.stdout.write("Senha demo: PassaMoz123!")
