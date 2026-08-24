from decimal import Decimal

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.models import PassengerProfile
from apps.bookings.models import Booking
from apps.tickets.models import Ticket
from apps.transporters.models import Transporter
from apps.trips.models import Trip


def is_staff(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff, login_url="/admin/login/")
def dashboard(request):
    now = timezone.now()
    paid = getattr(Booking.Status, "PAID", "paid")
    cancelled = getattr(Booking.Status, "CANCELLED", "cancelled")

    operators = (
        Transporter.objects.annotate(
            trip_count=Count("trips", distinct=True),
            ticket_count=Count("trips__bookings__ticket", distinct=True),
        ).order_by("name")[:20]
    )

    trips = (
        Trip.objects.select_related("route", "transporter")
        .filter(departure_at__gte=now)
        .order_by("departure_at")[:15]
    )

    context = {
        "stats": [
            ("Operadoras", Transporter.objects.count(),
             f"{Transporter.objects.filter(status='active').count()} ativas"),
            ("Passageiros", PassengerProfile.objects.count(), "contas cadastradas"),
            ("Viagens", Trip.objects.count(), "todas as viagens"),
            ("Bilhetes", Ticket.objects.count(), "bilhetes emitidos"),
        ],
        "operators": operators,
        "pending_operators": Transporter.objects.filter(status="pending").count(),
        "trips": trips,
        "passenger_count": PassengerProfile.objects.count(),
        "ticket_count": Ticket.objects.count(),
        "paid_bookings": Booking.objects.filter(status=paid).count(),
        "pending_bookings": Booking.objects.exclude(
            status__in=[paid, cancelled]
        ).count(),
        "memberships": [],
        "monthly_paid": Decimal("0"),
        "monthly_pending": Decimal("0"),
    }


    return render(request, "admin_dashboard.html", context)
