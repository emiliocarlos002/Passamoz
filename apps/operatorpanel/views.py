from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.bookings.models import Booking, Payment
from apps.bookings.services import confirm_payment
from apps.platform.models import MonthlySubscription
from apps.tickets.models import Ticket
from apps.transporters.models import PaymentAccount, Route, Transporter, Vehicle
from apps.trips.models import Trip, TripSeat
from apps.passengerpanel.services import create_ticket_artifacts
from apps.notifications.services import notify_payment_confirmed, notify_payment_rejected

from .forms import PaymentAccountForm, RouteForm, TripForm, VehicleForm


def get_operator(request):
    if not request.user.is_authenticated:
        return None
    transporter = getattr(request.user, "transporter_profile", None)
    if not transporter or transporter.status != Transporter.Status.ACTIVE or transporter.activation_required:
        return None
    return transporter


def operator_required(view):
    @login_required(login_url="/conta/entrar/")
    def wrapped(request, *args, **kwargs):
        transporter = get_operator(request)
        if transporter is None:
            raise Http404("Conta de operadora não encontrada ou ainda não está ativa.")
        request.transporter = transporter
        return view(request, *args, **kwargs)
    return wrapped


@operator_required
def dashboard(request):
    operator = request.transporter
    trips = operator.trips.all()
    bookings = Booking.objects.filter(trip__transporter=operator)
    subscriptions = operator.subscriptions.all()

    upcoming = (
        trips.select_related("route", "vehicle")
        .filter(departure_at__gte=timezone.now())
        .order_by("departure_at")[:10]
    )

    context = {
        "operator": operator,
        "stats": [
            ("Viagens", trips.count(), f"{trips.filter(status=Trip.Status.PUBLISHED).count()} publicadas"),
            ("Reservas", bookings.count(), f"{bookings.filter(status=Booking.Status.PAID).count()} pagas"),
            ("Bilhetes", Ticket.objects.filter(booking__trip__transporter=operator).count(), "emitidos"),
            ("Receita", bookings.filter(status=Booking.Status.PAID).aggregate(
                total=Sum("amount")
            )["total"] or 0, "MZN em reservas pagas"),
        ],
        "upcoming": upcoming,
        "pending_bookings": bookings.filter(status=Booking.Status.PENDING).count(),
        "available_seats": TripSeat.objects.filter(
            trip__transporter=operator,
            trip__status=Trip.Status.PUBLISHED,
            is_available=True,
        ).count(),
        "vehicles": operator.vehicles.filter(active=True).count(),
        "routes": operator.routes.filter(active=True).count(),
        "subscriptions": subscriptions.order_by("-reference_month")[:5],
    }
    return render(request, "operatorpanel/dashboard.html", context)


@operator_required
def route_list(request):
    routes = request.transporter.routes.order_by("origin", "destination")
    return render(request, "operatorpanel/routes.html", {"routes": routes, "operator": request.transporter})


@operator_required
def route_create(request):
    form = RouteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        route = form.save(commit=False)
        route.transporter = request.transporter
        route.save()
        messages.success(request, "Rota criada com sucesso.")
        return redirect("operator-route-list")
    return render(request, "operatorpanel/form.html", {
        "form": form, "title": "Nova rota", "back_url": "operator-route-list",
    })


@operator_required
def route_edit(request, pk):
    route = get_object_or_404(Route, pk=pk, transporter=request.transporter)
    form = RouteForm(request.POST or None, instance=route)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Rota atualizada.")
        return redirect("operator-route-list")
    return render(request, "operatorpanel/form.html", {
        "form": form, "title": "Editar rota", "back_url": "operator-route-list",
    })


@operator_required
@require_POST
def route_delete(request, pk):
    route = get_object_or_404(Route, pk=pk, transporter=request.transporter)
    route.active = False
    route.save(update_fields=["active"])
    messages.success(request, "Rota desativada.")
    return redirect("operator-route-list")


@operator_required
def vehicle_list(request):
    vehicles = request.transporter.vehicles.annotate(
        seat_count=Count("seats", filter=Q(seats__active=True))
    ).order_by("name")
    return render(request, "operatorpanel/vehicles.html", {
        "vehicles": vehicles, "operator": request.transporter,
    })


@operator_required
def vehicle_create(request):
    form = VehicleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        vehicle = form.save(commit=False)
        vehicle.transporter = request.transporter
        vehicle.save()
        messages.success(request, "Viatura criada com sucesso.")
        return redirect("operator-vehicle-list")
    return render(request, "operatorpanel/form.html", {
        "form": form, "title": "Nova viatura", "back_url": "operator-vehicle-list",
    })


@operator_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, transporter=request.transporter)
    form = VehicleForm(request.POST or None, instance=vehicle)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Viatura atualizada.")
        return redirect("operator-vehicle-list")
    return render(request, "operatorpanel/form.html", {
        "form": form, "title": "Editar viatura", "back_url": "operator-vehicle-list",
    })


@operator_required
@require_POST
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, transporter=request.transporter)
    vehicle.active = False
    vehicle.save(update_fields=["active"])
    messages.success(request, "Viatura desativada.")
    return redirect("operator-vehicle-list")


@operator_required
def trip_list(request):
    trips = request.transporter.trips.select_related(
        "route", "vehicle"
    ).order_by("-departure_at")
    return render(request, "operatorpanel/trips.html", {
        "trips": trips, "operator": request.transporter,
    })


@operator_required
def trip_create(request):
    form = TripForm(request.POST or None, transporter=request.transporter)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            trip = form.save(commit=False)
            trip.transporter = request.transporter
            trip.save()
            seats = trip.vehicle.seats.filter(active=True)
            TripSeat.objects.bulk_create(
                [TripSeat(trip=trip, seat=seat) for seat in seats],
                ignore_conflicts=True,
            )
        messages.success(request, "Viagem criada e lugares preparados.")
        return redirect("operator-trip-list")
    return render(request, "operatorpanel/form.html", {
        "form": form, "title": "Nova viagem", "back_url": "operator-trip-list",
    })


@operator_required
def trip_edit(request, pk):
    trip = get_object_or_404(Trip, pk=pk, transporter=request.transporter)
    form = TripForm(request.POST or None, instance=trip, transporter=request.transporter)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            trip = form.save()
            seats = trip.vehicle.seats.filter(active=True)
            TripSeat.objects.bulk_create(
                [TripSeat(trip=trip, seat=seat) for seat in seats],
                ignore_conflicts=True,
            )
        messages.success(request, "Viagem atualizada.")
        return redirect("operator-trip-list")
    return render(request, "operatorpanel/form.html", {
        "form": form, "title": "Editar viagem", "back_url": "operator-trip-list",
    })


@operator_required
@require_POST
def trip_cancel(request, pk):
    trip = get_object_or_404(Trip, pk=pk, transporter=request.transporter)
    if trip.bookings.filter(status=Booking.Status.PAID).exists():
        messages.error(request, "A viagem possui reservas pagas e não pode ser cancelada por aqui.")
        return redirect("operator-trip-list")
    trip.status = Trip.Status.CANCELLED
    trip.save(update_fields=["status"])
    messages.success(request, "Viagem cancelada.")
    return redirect("operator-trip-list")


@operator_required
def booking_list(request):
    bookings = (
        Booking.objects.filter(trip__transporter=request.transporter)
        .select_related("passenger", "trip__route", "trip_seat__seat")
        .prefetch_related("payments", "ticket")
        .order_by("-created_at")
    )
    status_filter = request.GET.get("status", "").strip()
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    query = request.GET.get("q", "").strip()
    if query:
        bookings = bookings.filter(
            Q(reference__icontains=query)
            | Q(passenger__first_name__icontains=query)
            | Q(passenger__last_name__icontains=query)
            | Q(passenger__email__icontains=query)
        )
    return render(request, "operatorpanel/bookings.html", {
        "bookings": bookings, "operator": request.transporter,
        "status_filter": status_filter, "query": query,
    })


@operator_required
def payment_accounts(request):
    accounts = request.transporter.payment_accounts.order_by("provider")
    form = PaymentAccountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        account = form.save(commit=False)
        account.transporter = request.transporter
        account.save()
        messages.success(request, "Conta de pagamento guardada.")
        return redirect("operator-payment-accounts")
    return render(request, "operatorpanel/payment_accounts.html", {
        "accounts": accounts, "form": form, "operator": request.transporter,
    })


@operator_required
@require_POST
def payment_account_toggle(request, pk):
    account = get_object_or_404(
        PaymentAccount, pk=pk, transporter=request.transporter
    )
    account.is_active = not account.is_active
    account.save(update_fields=["is_active"])
    messages.success(request, "Estado da conta de pagamento atualizado.")
    return redirect("operator-payment-accounts")


@operator_required
def subscription_list(request):
    subscriptions = request.transporter.subscriptions.order_by("-reference_month")
    return render(request, "operatorpanel/subscriptions.html", {
        "subscriptions": subscriptions, "operator": request.transporter,
    })


@operator_required
@require_POST
def payment_confirm(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related("booking__trip__transporter"),
        pk=pk, booking__trip__transporter=request.transporter,
    )
    booking = payment.booking
    if booking.expires_at and booking.expires_at <= timezone.now() and booking.status in {Booking.Status.PENDING, Booking.Status.PAYMENT_PROCESSING}:
        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(pk=booking.pk)
            booking.status = Booking.Status.EXPIRED
            booking.cancelled_at = timezone.now()
            booking.save(update_fields=["status", "cancelled_at"])
            trip_seat = TripSeat.objects.select_for_update().get(pk=booking.trip_seat_id)
            trip_seat.is_available = True
            trip_seat.save(update_fields=["is_available"])
        messages.error(request, "A reserva expirou e o lugar foi libertado.")
        return redirect("operator-booking-list")
    if payment.status == "rejected":
        messages.error(request, "Este pagamento já foi rejeitado.")
        return redirect("operator-booking-list")
    if booking.status in {Booking.Status.CANCELLED, Booking.Status.EXPIRED, Booking.Status.REFUNDED}:
        messages.error(request, "A reserva não pode mais ser paga.")
        return redirect("operator-booking-list")
    if payment.amount != booking.amount:
        payment.status = "rejected"
        payment.gateway_status = "amount_mismatch"
        payment.save(update_fields=["status", "gateway_status", "updated_at"])
        messages.error(request, "O valor do pagamento não corresponde ao valor da reserva.")
        return redirect("operator-booking-list")

    booking, ticket = confirm_payment(payment.pk)
    if not ticket:
        messages.error(request, "Não foi possível confirmar esta reserva.")
        return redirect("operator-booking-list")
    if not ticket.pdf:
        create_ticket_artifacts(ticket)
    notify_payment_confirmed(booking)
    messages.success(request, f"Pagamento confirmado. Bilhete {ticket.code} liberado para o passageiro.")
    return redirect("operator-booking-list")


@operator_required
@require_POST
def payment_reject(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related("booking__trip__transporter"),
        pk=pk,
        booking__trip__transporter=request.transporter,
    )

    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(pk=payment.pk)
        booking = Booking.objects.select_for_update().get(pk=payment.booking_id)

        if payment.status == "confirmed" or booking.status == Booking.Status.PAID:
            messages.error(request, "Um pagamento já confirmado não pode ser rejeitado aqui.")
            return redirect("operator-booking-list")

        if payment.status == "rejected":
            messages.info(request, "Este pagamento já foi rejeitado.")
            return redirect("operator-booking-list")

        payment.status = "rejected"
        payment.save(update_fields=["status"])

        if booking.status in {Booking.Status.PENDING, Booking.Status.PAYMENT_PROCESSING}:
            booking.status = Booking.Status.CANCELLED
            booking.save(update_fields=["status"])

            trip_seat = TripSeat.objects.select_for_update().get(
                pk=booking.trip_seat_id
            )
            trip_seat.is_available = True
            trip_seat.save(update_fields=["is_available"])

    notify_payment_rejected(booking)
    messages.success(request, "Pagamento rejeitado e lugar libertado.")
    return redirect("operator-booking-list")
